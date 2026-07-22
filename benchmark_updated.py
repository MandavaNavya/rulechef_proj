
"""
Iterative RuleChef Benchmark with Rule Inspection 

"""

import os
import re
import json
import time
import shutil
import pickle
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from rulechef import RuleChef, Task, TaskType
from google import genai


#  DATASET LOADER

def load_data(csv_path, selected_diseases=None, test_size=0.30,
              val_size=0.50, random_state=42):
    df = pd.read_csv(csv_path)
    
    # Convert disease labels to lowercase so that
    # "Psoriasis" and "psoriasis" become identical.
    
    df["label"] = df["label"].str.lower().str.strip()
    
    # Clean the symptom text as well.
    # Removing whitespace avoids unnecessary mismatches.
    df["text"] = df["text"].str.lower().str.strip()
    
    """If the user didn't explicitly choose diseases, automatically select the 
    two most frequent classes.
    This allows binary classification experiments."""
    if selected_diseases is None:
        selected_diseases = df["label"].value_counts().head(2).index.tolist()

    
    df_binary = df[df["label"].isin(selected_diseases)].copy()

    """Split the dataset into Train = 70% Validation = 15% Test = 15%"""
    train_df, temp_df = train_test_split(
        df_binary,
        test_size=test_size,
        stratify=df_binary["label"],
        random_state=random_state,
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=val_size,
        stratify=temp_df["label"],
        random_state=random_state,
    )
    return train_df, val_df, test_df, selected_diseases


#  GEMINI CLIENT

class GeminiClient:
    def __init__(self, api_key):
        #Create Gemini client
        self.client = genai.Client(api_key=api_key)
         # Choose the Gemini model.
        self.active_model = "gemini-2.5-flash"
        ## Create a Chat object so RuleChef can call
        self.chat = self.Chat(self)

    def set_mode(self, mode=None):
        print(f"\n[Client] Using model: {self.active_model}")

    class Chat:
        def __init__(self, parent):
            self.parent = parent
            self.completions = self.Completions(parent)

        class Completions:
            def __init__(self, parent):
                self.parent = parent
                
                """ Convert the OpenAI message list into one prompt string for Gemini."""

            def create(self, model=None, messages=None, **kwargs):
                prompt = ""
                for m in messages:
                    prompt += f"{m.get('role','').upper()}: {m.get('content','')}\n"
                    
                """  Retry up to three times if Gemini temporarily fails."""
                for attempt in range(3):
                    try:
                        response = self.parent.client.models.generate_content(
                            model=self.parent.active_model,
                            contents=prompt,
                        )
                        """  
                         RuleChef expects the response format:
                         response.choices[0].message.content
                        Gemini returns something different.
                        Therefore we wrap the Gemini response inside an OpenAI-compatible object.
                       """
                        class Result:
                            def __init__(self, text):
                                self.choices = [
                                    type("Choice", (), {
                                        "message": type("Msg", (), {
                                            "content": text
                                        })
                                    })
                                ]
                        return Result(response.text)
                    #retry after waiting
                    except Exception as e:
                        if attempt < 2:
                            time.sleep((attempt + 1) * 5)
                        else:
                            raise e

"""This class loads the learned rules from the JSON file and
applies them to new symptom descriptions.

Responsibilities:

1. Load all regex rules
2. Compile regex patterns (faster matching)
3. Sort rules by priority
4. Predict the disease label for new text"""

#  RULE ENGINE

class RuleEngine:
    def __init__(self, rules_json):
        with open(rules_json, "r", encoding="utf8") as f:
            data = json.load(f)
        """ RuleChef may save rules either as:
        {"rules":[...]} or simply: [...] Handle both formats."""
        if isinstance(data, dict):
            rules = data.get("rules", [])
        elif isinstance(data, list):
            rules = data
        else:
            raise ValueError("Invalid rule file.")
        # Store compiled rules here.
        self.rules = []
        #Convert every JSON rule into an executable rule.
        for idx, rule in enumerate(rules):
            pattern = rule.get("content") or rule.get("pattern")
            if pattern is None:
                continue
            if "output_template" in rule:
                label = rule["output_template"].get("label")
            else:
                label = rule.get("label")
            # Store everything needed during prediction.
            self.rules.append({
                "id": rule.get("id", f"rule_{idx+1}"),
                "name": rule.get("name", f"Rule {idx+1}"),
                "label": label,
                # Higher priority rules are preferred
                # when multiple rules match.
                "priority": rule.get("priority", 0),
                "pattern": re.compile(pattern, re.IGNORECASE),
                "pattern_string": pattern
            })
             # Highest priority rule should be checked first.
        self.rules.sort(key=lambda x: x["priority"], reverse=True)

    def predict(self, text):
        # Stores every rule that matches the input text.
        matches = []
        # Test every rule against the symptom description.
        for rule in self.rules:

            if rule["pattern"].search(text):
                matches.append(rule)
        # No rule matched.
        if not matches:
            return None, []
        
        best = max(matches, key=lambda r: r["priority"])

        return best, matches

"""EVALUATION

Tests every sample in the test dataset.
Computes:
• Accuracy
• Precision
• Recall
• F1
• Coverage
• Confusion Matrix
• Per-rule statistics """


#  EVALUATION FUNCTIONS 

def evaluate(engine, test_df, labels):
    y_true = []
    y_pred = []
     # Store prediction details.
    predictions = []
    # Every rule gets its own statistics dictionary.
    rule_statistics = {}
    for rule in engine.rules:
        rule_statistics[rule["id"]] = {
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "label": rule["label"],
            # Number of samples matched
            "matched": 0,
            "correct": 0,
            "incorrect": 0,
            "false_positive": 0,
            "false_negative": 0,
            "examples_correct": [],
            "examples_wrong": []
        }
    # Evaluate every sample.
    for _, row in test_df.iterrows():
        text = row["text"]
        truth = row["label"]
        # Run the rule engine.
        matched_rule, fired_rules = engine.predict(text)
        # If no rule matched,
        # prediction becomes UNKNOWN.
        if matched_rule is None:
            pred = "unknown"
            rule_used = None
        else:
            pred = matched_rule["label"]
            rule_used = matched_rule["id"]
        # Save prediction information.
        y_true.append(truth)
        y_pred.append(pred)
        predictions.append({
            "text": text,
            "true_label": truth,
            "predicted_label": pred,
            "rule": rule_used
        })
        # Every fired rule receives statistics,not only the winning rule.
        if matched_rule is not None:
            for r in fired_rules:

                stat = rule_statistics[r["id"]]

                stat["matched"] += 1

                if r["label"] == truth:

                    stat["correct"] += 1

                else:

                    stat["incorrect"] += 1
            # Save a few example sentences
            # for report generation.
            if pred == truth:
                stat["correct"] += 1
                if len(stat["examples_correct"]) < 5:
                    stat["examples_correct"].append(text)
            else:
                stat["incorrect"] += 1
                stat["false_positive"] += 1
                if len(stat["examples_wrong"]) < 5:
                    stat["examples_wrong"].append({
                        "text": text,
                        "true": truth,
                        "predicted": pred
                    })
    # Compute coverage :   Ignore UNKNOWN predictions.
    known = [(t, p) for t, p in zip(y_true, y_pred) if p != "unknown"]
    # Coverage tells us:"How much of the test set is covered by rules?"
    coverage = len(known) / len(y_true) if y_true else 0

    if not known:
        metrics = {
            "coverage": coverage,
            "accuracy": None,
            "precision_macro": None, "recall_macro": None, "f1_macro": None,
            "precision_micro": None, "recall_micro": None, "f1_micro": None,
            "precision_weighted": None, "recall_weighted": None, "f1_weighted": None,
            "covered_samples": 0,
            "total_samples": len(y_true)
        }
        return metrics, None, [], [], predictions

    y_true_known = [x[0] for x in known]
    y_pred_known = [x[1] for x in known]

    acc = accuracy_score(y_true_known, y_pred_known)
    pm, rm, fm, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="macro", zero_division=0
    )
    pim, rim, fim, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="micro", zero_division=0
    )
    pw, rw, fw, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="weighted", zero_division=0
    )

    metrics = {
        "coverage": coverage,
        "covered_samples": len(known),
        "total_samples": len(y_true),
        "accuracy": acc,
        "precision_macro": pm,
        "recall_macro": rm,
        "f1_macro": fm,
        "precision_micro": pim,
        "recall_micro": rim,
        "f1_micro": fim,
        "precision_weighted": pw,
        "recall_weighted": rw,
        "f1_weighted": fw,
    }

    unique_labels = sorted(set(y_true_known + y_pred_known))
    cm = confusion_matrix(y_true_known, y_pred_known, labels=unique_labels)

    per_class = []
    for label in unique_labels:
        tp = np.sum((np.array(y_true_known) == label) & (np.array(y_pred_known) == label))
        fp = np.sum((np.array(y_true_known) != label) & (np.array(y_pred_known) == label))
        fn = np.sum((np.array(y_true_known) == label) & (np.array(y_pred_known) != label))
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        per_class.append({
            "label": label,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "precision": prec,
            "recall": rec,
            "f1": f1
        })

    final_rule_stats = []
    for rid, data in rule_statistics.items():
        matched = data["matched"]
        correct = data["correct"]
        incorrect = data["incorrect"]
        precision = correct / matched if matched else 0
        total_true = len(test_df[test_df["label"] == data["label"]])
        recall = correct / total_true if total_true else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        final_rule_stats.append({
            "rule_id": rid,
            "rule_name": data["rule_name"],
            "label": data["label"],
            "matched": matched,
            "correct": correct,
            "incorrect": incorrect,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "coverage": matched / len(test_df) if len(test_df) > 0 else 0,
            "false_positive": data["false_positive"],
            "examples_correct": data["examples_correct"],
            "examples_wrong": data["examples_wrong"]
        })

    final_rule_stats.sort(key=lambda x: (x["precision"], x["coverage"]), reverse=True)
    return metrics, cm, per_class, final_rule_stats, predictions

"""RULE QUALITY ANALYSIS:

After evaluation, every rule has statistics such as:
Precision
Recall
Coverage
Correct predictions
Incorrect predictions

This function converts those statistics into an
easy-to-understand quality score.
"""

def analyze_rule_quality(rule_stats):
    analysis = []
     # Examine every learned rule individually.
    for rule in rule_stats:
        score = 100
        suggestions = []
        # Low precision means the rule predicts the wrong disease frequently.
        if rule["precision"] < 0.50:
            score -= 35
            suggestions.append("Precision is very low. Rule is likely too generic.")
        elif rule["precision"] < 0.70:
            score -= 20
            suggestions.append("Increase specificity to reduce false positives.")
        # Low recall means the rule misses many true disease cases.
        if rule["recall"] < 0.40:
            score -= 20
            suggestions.append("Recall is low. Rule misses many true examples.")
        # Coverage tells how frequently the rule fires.
        if rule["coverage"] < 0.05:
            score -= 10
            suggestions.append("Rule rarely activates.")
        elif rule["coverage"] > 0.60:
            score -= 15
            suggestions.append("Rule activates too frequently.")
         # More incorrect predictions than correct ones indicates a poor-quality rule.
        if rule["incorrect"] > rule["correct"]:
            score -= 25
            suggestions.append("Produces more wrong than correct predictions.")
        if rule["false_positive"] > 5:
            score -= 15
            suggestions.append("Large number of false positives.")
        score = max(score, 0)
        if score >= 90:
            quality = "Excellent"
        elif score >= 75:
            quality = "Good"
        elif score >= 60:
            quality = "Fair"
        else:
            quality = "Poor"
        analysis.append({
            "rule_id": rule["rule_id"],
            "rule_name": rule["rule_name"],
            "label": rule["label"],
            "quality": quality,
            "quality_score": score,
            "suggestions": "; ".join(suggestions)
        })
    return analysis

# Detect the week rules
def detect_weak_rules(rule_stats):
    weak = [r for r in rule_stats if (r["precision"] < 0.70 or
                                      r["incorrect"] > r["correct"] or
                                      r["coverage"] > 0.60)]
    weak.sort(key=lambda x: x["precision"])
    return weak

# Detect the strong rules
def detect_strong_rules(rule_stats):
    good = [r for r in rule_stats if r["precision"] >= 0.90 and r["coverage"] >= 0.05]
    good.sort(key=lambda x: x["precision"], reverse=True)
    return good


def analyze_errors(predictions):
    errors = []
    for pred in predictions:
        if pred["predicted_label"] == "unknown":
            continue
        if pred["true_label"] != pred["predicted_label"]:
            errors.append({
                "text": pred["text"],
                "true_label": pred["true_label"],
                "predicted_label": pred["predicted_label"],
                "rule": pred["rule"]
            })
    return errors


def build_improvement_suggestions(rule_stats):
    suggestions = []
    for rule in rule_stats:
        text = []
        if rule["precision"] < 0.60:
            text.append("Require additional symptoms before firing.")
        if rule["coverage"] > 0.50:
            text.append("Current rule is too broad.")
        if rule["recall"] < 0.50:
            text.append("Consider adding alternative symptom patterns.")
        if rule["incorrect"] > rule["correct"]:
            text.append("Inspect misclassified examples and refine regex.")
        if not text:
            text.append("Rule looks stable.")
        suggestions.append({
            "rule_id": rule["rule_id"],
            "rule_name": rule["rule_name"],
            "recommendation": " ".join(text)
        })
    return suggestions



# REPORT GENERATION

def generate_reports(metrics, cm, per_class, rule_stats, predictions,
                     labels, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    quality = analyze_rule_quality(rule_stats)
    weak_rules = detect_weak_rules(rule_stats)
    strong_rules = detect_strong_rules(rule_stats)
    errors = analyze_errors(predictions)
    suggestions = build_improvement_suggestions(rule_stats)

    report_json = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "labels": labels,
        "confusion_matrix": cm.tolist() if cm is not None else [],
        "per_class": per_class,
        "rule_statistics": rule_stats,
        "rule_quality": quality,
        "rule_suggestions": suggestions,
        "weak_rules": weak_rules,
        "strong_rules": strong_rules,
        "misclassifications": errors
    }
    with open(output_dir / "report.json", "w") as f:
        json.dump(report_json, f, indent=2)

    pd.DataFrame(per_class).to_csv(output_dir / "per_class.csv", index=False)

    pd.DataFrame(rule_stats).drop(
        columns=["examples_correct", "examples_wrong"],
        errors="ignore"
    ).to_csv(output_dir / "rule_stats.csv", index=False)

    pd.DataFrame(quality).to_csv(output_dir / "rule_quality.csv", index=False)
    pd.DataFrame(suggestions).to_csv(output_dir / "rule_suggestions.csv", index=False)

    pd.DataFrame(weak_rules).drop(
        columns=["examples_correct", "examples_wrong"],
        errors="ignore"
    ).to_csv(output_dir / "weak_rules.csv", index=False)

    pd.DataFrame(strong_rules).drop(
        columns=["examples_correct", "examples_wrong"],
        errors="ignore"
    ).to_csv(output_dir / "strong_rules.csv", index=False)

    pd.DataFrame(errors).to_csv(output_dir / "misclassified.csv", index=False)

    rows = []
    for rule in rule_stats:
        for ex in rule["examples_correct"]:
            rows.append({
                "rule_id": rule["rule_id"],
                "rule_name": rule["rule_name"],
                "type": "correct",
                "example": ex,
                "true": "",
                "predicted": ""
            })
        for ex in rule["examples_wrong"]:
            rows.append({
                "rule_id": rule["rule_id"],
                "rule_name": rule["rule_name"],
                "type": "incorrect",
                "example": ex["text"],
                "true": ex["true"],
                "predicted": ex["predicted"]
            })
    pd.DataFrame(rows).to_csv(output_dir / "rule_examples.csv", index=False)

    if cm is not None:
        df_cm = pd.DataFrame(cm, index=sorted(labels), columns=sorted(labels))
        df_cm.to_csv(output_dir / "confusion_matrix.csv")

    md = []
    md.append("# RuleChef Benchmark Report\n")
    md.append(f"Generated: {datetime.now()}\n")
    md.append("## Overall Metrics\n")
    md.append("|Metric|Value|")
    md.append("|---|---|")
    for k, v in metrics.items():
        if isinstance(v, float):
            md.append(f"|{k}|{v:.4f}|")
        else:
            md.append(f"|{k}|{v}|")

    md.append("\n## Top Rules\n")
    md.append("|Rule|Precision|Recall|Coverage|")
    md.append("|---|---|---|---|")
    for r in strong_rules[:10]:
        md.append(f"|{r['rule_name']}|{r['precision']:.3f}|{r['recall']:.3f}|{r['coverage']:.3f}|")

    md.append("\n## Weak Rules\n")
    md.append("|Rule|Precision|Recall|Coverage|")
    md.append("|---|---|---|---|")
    for r in weak_rules:
        md.append(f"|{r['rule_name']}|{r['precision']:.3f}|{r['recall']:.3f}|{r['coverage']:.3f}|")

    md.append("\n## Rule Improvement Suggestions\n")
    for s in suggestions:
        md.append(f"### {s['rule_name']}\n")
        md.append(f"- {s['recommendation']}\n")

    md.append("\n## Misclassified Samples\n")
    for e in errors[:20]:
        md.append(f"**Rule:** {e['rule']}\n")
        md.append(f"- True: {e['true_label']}\n")
        md.append(f"- Predicted: {e['predicted_label']}\n")
        md.append(f"- Text: {e['text']}\n")

    md.append("\n## Rule Quality\n")
    md.append("|Rule|Quality|Score|")
    md.append("|---|---|---|")
    for q in quality:
        md.append(f"|{q['rule_name']}|{q['quality']}|{q['quality_score']}|")

    with open(output_dir / "report.md", "w", encoding="utf8") as f:
        f.write("\n".join(md))

    print("\n" + "="*80)
    print("REPORTS GENERATED")
    print("="*80)
    print("report.json")
    print("report.md")
    print("rule_stats.csv")
    print("rule_quality.csv")
    print("rule_suggestions.csv")
    print("weak_rules.csv")
    print("strong_rules.csv")
    print("misclassified.csv")
    print("rule_examples.csv")
    print("per_class.csv")
    print("confusion_matrix.csv")
    print(f"\nSaved to: {output_dir}")



# MAIN PIPELINE (with fixed rule extraction)

def main():
    API_KEY = "YourAPIKEY"         
    DATASET_PATH = "Symptom2Disease.csv"
    RULES_DIR = Path("benchmark_learned_rules")
    REPORTS_DIR = Path("benchmark_reports")
    STORAGE_PATH = "./rulechef_binary_updated"

    if os.path.exists(STORAGE_PATH):
        shutil.rmtree(STORAGE_PATH)

    RULES_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    print("Loading dataset...")
    train_df, val_df, test_df, selected_diseases = load_data(
        DATASET_PATH,
        test_size=0.30,
        val_size=0.50,
        random_state=42
    )
    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    print(f"Selected diseases: {selected_diseases}")

    task = Task(
        name="Disease Classification",
        description="Classify disease based on symptoms",
        input_schema={"text": "str"},
        output_schema={"label": "str"},
        type=TaskType.CLASSIFICATION,
        text_field="text",
    )
    client = GeminiClient(api_key=API_KEY)
    chef = RuleChef(task, client, storage_path=STORAGE_PATH)

    #  Learn rules incrementally 
    examples_per_class = 15
    rule_learning_df = (
        train_df
        .groupby("label", group_keys=False)
        .sample(n=examples_per_class, random_state=42)
        .sort_values("label")
        .reset_index(drop=True)
    )
    batches = [
        pd.concat([g.iloc[:5] for _, g in rule_learning_df.groupby("label")]),
        pd.concat([g.iloc[5:10] for _, g in rule_learning_df.groupby("label")]),
        pd.concat([g.iloc[10:15] for _, g in rule_learning_df.groupby("label")]),
    ]

    client.set_mode("synthesis")
    all_rules_text = []
    learned_rules = None

    for i, batch in enumerate(batches, 1):
        print(f"\n===== BATCH {i} =====")
        for _, row in batch.iterrows():
            if pd.isna(row["text"]) or pd.isna(row["label"]):
                continue
            chef.add_example({"text": str(row["text"])}, {"label": str(row["label"])})

        start = time.time()
        rules = chef.learn_rules()
        learned_rules = rules
        print("\nTYPE OF RULES")
        print(type(rules))

        print("\nDIR OF RULES")
        print(dir(rules))

        print("\nRULES OBJECT")
        print(rules)
        elapsed = time.time() - start
        print(f"Rule learning time: {elapsed:.2f}s")
        

        rule_file = RULES_DIR / f"batch_{i}_rules.txt"
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write(str(rules))
        print(f"Saved batch rules to {rule_file}")
        all_rules_text.append((i, str(rules)))

# EXTRACT RULES


    rules_list = []

    raw_rules = learned_rules

    # RuleChef returns:
    # ([Rule(...), Rule(...)], EvalResult(...))

    if isinstance(raw_rules, tuple):

        raw_rules = raw_rules[0]

    print("\nNumber of learned rules:", len(raw_rules))

    for idx, rule in enumerate(raw_rules):

        print(f"Extracting rule {idx+1}: {rule.name}")

        rules_list.append({

            "id": rule.id,

            "name": rule.name,

            "description": rule.description,

            "pattern": rule.content,

            "priority": rule.priority,

            "label": rule.output_template["label"]

        })

    print("Extracted", len(rules_list), "rules")

    # Save rules JSON
    rules_json_path = RULES_DIR / "final_rules.json"
    with open(rules_json_path, "w", encoding="utf-8") as f:
        json.dump({"rules": rules_list}, f, indent=2)
    print(f"\nSaved final rules JSON to {rules_json_path} with {len(rules_list)} rules.")
    print(json.dumps(rules_list, indent=2))
    # ---- EVALUATE ----
    engine = RuleEngine(rules_json_path)
    print(f"\nLoaded {len(engine.rules)} rules for evaluation.")

    print("\n===== EVALUATING ON TEST SET =====")
    metrics, cm, per_class, rule_stats, predictions = evaluate(
        engine, test_df, selected_diseases
    )

    print(f"Coverage: {metrics['covered_samples']}/{metrics['total_samples']} ({metrics['coverage']:.2%})")
    if metrics['accuracy'] is not None:
        print(f"Accuracy (on known): {metrics['accuracy']:.4f}")
        print(f"F1 macro: {metrics['f1_macro']:.4f}")

    generate_reports(
        metrics, cm, per_class, rule_stats, predictions,
        selected_diseases, REPORTS_DIR
    )

    print("\n Benchmark completed. Inspect reports in 'benchmark_reports/'.")


if __name__ == "__main__":
    main()