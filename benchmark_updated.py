
import os
import re
import json
import time
import shutil
import html
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



# CONFIGURATION


API_KEY = "Your_API_Key"

DATASET_PATH = "Symptom2Disease.csv"

RULES_DIR = Path("benchmark_learned_rules")
REPORTS_DIR = Path("benchmark_reports")

STORAGE_PATH = "./rulechef_multiclass_updated"

RANDOM_STATE = 42


# CLASS SELECTION


SELECTED_DISEASES = None

NUMBER_OF_CLASSES = 4

# Number of examples used to learn rules per disease.
# These examples come ONLY from the training set.
EXAMPLES_PER_CLASS = 15

# Dataset split:
# 70% train
# 15% validation
# 15% test
TEST_SIZE = 0.30
VALIDATION_FROM_TEMP = 0.50



# DATASET LOADER


def load_data(
    csv_path,
    selected_diseases=None,
    number_of_classes=5,
    test_size=0.30,
    val_size=0.50,
    random_state=42,):
    

    print("\nLoading dataset...")
    df = pd.read_csv(csv_path)

   
    # Check required columns
   

    required_columns = {"label", "text"}

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    
    # Clean labels and text
    
    df["label"] = (
        df["label"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["text"] = (
        df["text"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # Remove empty rows
    df = df[
        (df["label"] != "") &
        (df["text"] != "")
    ].copy()

    
    # Remove accidental "nan" strings
   

    df = df[
        (df["label"] != "nan") &
        (df["text"] != "nan")
    ].copy()

    
    # Determine classes
    

    class_counts = df["label"].value_counts()

    print("\nClass distribution:")
    print(class_counts)

    if selected_diseases is None:

        selected_diseases = (
            class_counts
            .head(number_of_classes)
            .index
            .tolist()
        )

    else:

        selected_diseases = [
            str(x).lower().strip()
            for x in selected_diseases
        ]

    if len(selected_diseases) != number_of_classes:
        print(
            f"\nWarning: {len(selected_diseases)} classes selected "
            f"instead of requested {number_of_classes}."
        )

    
    # Check selected classes exist


    missing_classes = [
        disease
        for disease in selected_diseases
        if disease not in class_counts.index
    ]

    if missing_classes:
        raise ValueError(
            f"The following selected classes are not present "
            f"in the dataset: {missing_classes}"
        )

   
    # Select only requested classes
  

    df_selected = df[
        df["label"].isin(selected_diseases)
    ].copy()

    # Preserve a clean class ordering
    selected_diseases = list(selected_diseases)

    print("\nSelected classes:")
    for disease in selected_diseases:
        count = len(
            df_selected[df_selected["label"] == disease]
        )
        print(f"  {disease}: {count} samples")

    
    # Train / validation / test split
    

    train_df, temp_df = train_test_split(
        df_selected,
        test_size=test_size,
        stratify=df_selected["label"],
        random_state=random_state,
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=val_size,
        stratify=temp_df["label"],
        random_state=random_state,
    )

    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    print("\nDataset split:")
    print(f"  Train:      {len(train_df)}")
    print(f"  Validation: {len(val_df)}")
    print(f"  Test:       {len(test_df)}")

    print("\nTrain distribution:")
    print(train_df["label"].value_counts())

    print("\nValidation distribution:")
    print(val_df["label"].value_counts())

    print("\nTest distribution:")
    print(test_df["label"].value_counts())

    return (
        train_df,
        val_df,
        test_df,
        selected_diseases,
    )


# GEMINI CLIENT

class GeminiClient:

    def __init__(self, api_key):

        self.client = genai.Client(
            api_key=api_key
        )

        self.active_model = "gemini-2.5-flash"

        self.chat = self.Chat(self)

    def set_mode(self, mode=None):

        print(
            f"\n[Client] Using model: "
            f"{self.active_model}"
        )

    class Chat:

        def __init__(self, parent):

            self.parent = parent
            self.completions = self.Completions(
                parent
            )

        class Completions:

            def __init__(self, parent):

                self.parent = parent

            def create(
                self,
                model=None,
                messages=None,
                **kwargs,
            ):

                prompt = ""

                if messages:

                    for message in messages:

                        prompt += (
                            f"{message.get('role', '').upper()}: "
                            f"{message.get('content', '')}\n"
                        )

                
                # Retry Gemini API calls
                

                for attempt in range(3):

                    try:

                        response = (
                            self.parent.client
                            .models
                            .generate_content(
                                model=self.parent.active_model,
                                contents=prompt,
                            )
                        )

                        class Result:

                            def __init__(self, text):

                                self.choices = [
                                    type(
                                        "Choice",
                                        (),
                                        {
                                            "message": type(
                                                "Msg",
                                                (),
                                                {
                                                    "content": text
                                                },
                                            )
                                        },
                                    )
                                ]

                        return Result(
                            response.text
                        )

                    except Exception as e:

                        if attempt < 2:

                            wait_time = (
                                (attempt + 1) * 5
                            )

                            print(
                                f"Gemini request failed. "
                                f"Retrying in "
                                f"{wait_time}s..."
                            )

                            time.sleep(wait_time)

                        else:

                            raise e



# RULE ENGINE


class RuleEngine:

    def __init__(self, rules_json):

        with open(
            rules_json,
            "r",
            encoding="utf8",
        ) as f:

            data = json.load(f)

        if isinstance(data, dict):

            rules = data.get(
                "rules",
                []
            )

        elif isinstance(data, list):

            rules = data

        else:

            raise ValueError(
                "Invalid rule file."
            )

        self.rules = []

        for idx, rule in enumerate(rules):

            pattern = (
                rule.get("content")
                or rule.get("pattern")
            )

            if pattern is None:
                continue

            
            # Determine output label
            

            if "output_template" in rule:

                output_template = (
                    rule.get("output_template")
                    or {}
                )

                label = output_template.get(
                    "label"
                )

            else:

                label = rule.get(
                    "label"
                )

            
            # Compile regex
            

            try:

                compiled_pattern = re.compile(
                    pattern,
                    re.IGNORECASE
                )

            except re.error as e:

                print(
                    f"\nWARNING: Could not compile rule "
                    f"{rule.get('id', idx)}"
                )

                print(
                    f"Pattern: {pattern}"
                )

                print(
                    f"Regex error: {e}"
                )

                continue

            self.rules.append(
                {
                    "id": rule.get(
                        "id",
                        f"rule_{idx + 1}"
                    ),

                    "name": rule.get(
                        "name",
                        f"Rule {idx + 1}"
                    ),

                    "description": rule.get(
                        "description",
                        ""
                    ),

                    "label": (
                        str(label).lower().strip()
                        if label is not None
                        else None
                    ),

                    "priority": rule.get(
                        "priority",
                        0
                    ),

                    "pattern": compiled_pattern,

                    "pattern_string": pattern,
                }
            )

        # Highest priority first
        self.rules.sort(
            key=lambda x: x["priority"],
            reverse=True,
        )

    def predict(self, text):

        matches = []

        for rule in self.rules:

            if rule["pattern"].search(
                text
            ):

                matches.append(rule)

        if not matches:

            return None, []

        best = max(
            matches,
            key=lambda r: r["priority"]
        )

        return best, matches



# RULE EXTRACTION


def extract_rules_from_rulechef(
    learned_rules
):
    """
    Convert RuleChef's Rule objects into
    a JSON-serializable representation.
    """

    raw_rules = learned_rules

    # RuleChef may return:
    #
    # ([Rule(...), Rule(...)], EvalResult(...))
    #
    if isinstance(raw_rules, tuple):

        raw_rules = raw_rules[0]

    if raw_rules is None:

        raise ValueError(
            "RuleChef returned no rules."
        )

    print(
        f"\nNumber of learned rules: "
        f"{len(raw_rules)}"
    )

    rules_list = []

    for idx, rule in enumerate(raw_rules):

        print(
            f"Extracting rule {idx + 1}: "
            f"{getattr(rule, 'name', 'Unnamed rule')}"
        )

        output_template = getattr(
            rule,
            "output_template",
            {}
        )

        if output_template is None:
            output_template = {}

        label = output_template.get(
            "label"
        )

        if label is not None:

            label = (
                str(label)
                .lower()
                .strip()
            )

        rules_list.append(
            {
                "id": getattr(
                    rule,
                    "id",
                    f"rule_{idx + 1}"
                ),

                "name": getattr(
                    rule,
                    "name",
                    f"Rule {idx + 1}"
                ),

                "description": getattr(
                    rule,
                    "description",
                    ""
                ),

                "pattern": getattr(
                    rule,
                    "content",
                    ""
                ),

                "priority": getattr(
                    rule,
                    "priority",
                    0
                ),

                "label": label,
            }
        )

    return rules_list



# RULE STATISTICS INITIALIZATION


def initialize_rule_statistics(
    engine
):
    """
    Create a statistics dictionary for each rule.
    """

    statistics = {}

    for rule in engine.rules:

        statistics[rule["id"]] = {

            "rule_id": rule["id"],

            "rule_name": rule["name"],

            "label": rule["label"],

            "description": rule["description"],

            "priority": rule["priority"],

            "pattern": rule["pattern_string"],

            "matched": 0,

            "winning_predictions": 0,

            "true_positive": 0,

            "false_positive": 0,

            "examples_true_positive": [],

            "examples_false_positive": [],
        }

    return statistics



# EVALUATION


def evaluate(
    engine,
    df,
    labels,
    dataset_name="test",
    max_examples_per_rule=10,
):
    """
    Evaluate the rule engine.

    Important distinction:

    matched:
        The regex fired on the sample.

    winning_predictions:
        This rule was the highest-priority matching rule.

    true_positive:
        The rule won and predicted the correct disease.

    false_positive:
        The rule won but predicted the wrong disease.

    This avoids the double-counting problem in the original
    implementation.
    """

    y_true = []
    y_pred = []

    predictions = []

    rule_statistics = (
        initialize_rule_statistics(engine)
    )

    
    # Evaluate every sample
    

    for _, row in df.iterrows():

        text = str(row["text"])

        truth = str(
            row["label"]
        ).lower().strip()

        matched_rule, fired_rules = (
            engine.predict(text)
        )

        
        # Unknown prediction
        

        if matched_rule is None:

            pred = "unknown"
            winning_rule_id = None
            winning_rule_name = None

        else:

            pred = str(
                matched_rule["label"]
            ).lower().strip()

            winning_rule_id = (
                matched_rule["id"]
            )

            winning_rule_name = (
                matched_rule["name"]
            )

        y_true.append(truth)
        y_pred.append(pred)
        
        # Update rule "matched" statistics
      
        for rule in fired_rules:

            stat = rule_statistics[
                rule["id"]
            ]

            stat["matched"] += 1

        # Update ONLY the winning rule for TP/FP
    
        if matched_rule is not None:

            stat = rule_statistics[
                matched_rule["id"]
            ]

            stat["winning_predictions"] += 1

            if pred == truth:

                stat["true_positive"] += 1

                if (
                    len(
                        stat[
                            "examples_true_positive"
                        ]
                    )
                    < max_examples_per_rule
                ):

                    stat[
                        "examples_true_positive"
                    ].append(
                        {
                            "text": text,
                            "true": truth,
                            "predicted": pred,
                        }
                    )

            else:

                stat["false_positive"] += 1

                if (
                    len(
                        stat[
                            "examples_false_positive"
                        ]
                    )
                    < max_examples_per_rule
                ):

                    stat[
                        "examples_false_positive"
                    ].append(
                        {
                            "text": text,
                            "true": truth,
                            "predicted": pred,
                        }
                    )

        # Save prediction
    
        predictions.append(
            {
                "dataset": dataset_name,

                "text": text,

                "true_label": truth,

                "predicted_label": pred,

                "correct": (
                    pred == truth
                ),

                "winning_rule_id":
                    winning_rule_id,

                "winning_rule_name":
                    winning_rule_name,

                "all_fired_rules":
                    [
                        r["id"]
                        for r in fired_rules
                    ],
            }
        )

    # METRICS

    total = len(y_true)

    known_mask = [
        prediction != "unknown"
        for prediction in y_pred
    ]

    known_count = sum(
        known_mask
    )

    coverage = (
        known_count / total
        if total > 0
        else 0
    )

   
    # Metrics including UNKNOWN as a failure
    
    # This is the most honest overall measurement.
  

    overall_accuracy = (
        accuracy_score(
            y_true,
            y_pred
        )
        if total > 0
        else 0
    )

    overall_precision_macro, overall_recall_macro, overall_f1_macro, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            average="macro",
            zero_division=0,
        )
    )

    overall_precision_weighted, overall_recall_weighted, overall_f1_weighted, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0,
        )
    )
    
    # Metrics on covered samples only
  
    covered_pairs = [
        (truth, pred)
        for truth, pred in zip(
            y_true,
            y_pred
        )
        if pred != "unknown"
    ]

    if covered_pairs:

        covered_true = [
            x[0]
            for x in covered_pairs
        ]

        covered_pred = [
            x[1]
            for x in covered_pairs
        ]

        covered_accuracy = (
            accuracy_score(
                covered_true,
                covered_pred
            )
        )

        covered_precision_macro, covered_recall_macro, covered_f1_macro, _ = (
            precision_recall_fscore_support(
                covered_true,
                covered_pred,
                labels=labels,
                average="macro",
                zero_division=0,
            )
        )

        covered_precision_weighted, covered_recall_weighted, covered_f1_weighted, _ = (
            precision_recall_fscore_support(
                covered_true,
                covered_pred,
                labels=labels,
                average="weighted",
                zero_division=0,
            )
        )

    else:

        covered_accuracy = None

        covered_precision_macro = None
        covered_recall_macro = None
        covered_f1_macro = None

        covered_precision_weighted = None
        covered_recall_weighted = None
        covered_f1_weighted = None
 
    # METRICS DICTIONARY
    metrics = {

        "dataset": dataset_name,

        "total_samples": total,

        "covered_samples": known_count,

        "unknown_samples": total - known_count,

        "coverage": coverage,

        # Honest overall metrics
        "overall_accuracy": overall_accuracy,

        "overall_precision_macro":
            overall_precision_macro,

        "overall_recall_macro":
            overall_recall_macro,

        "overall_f1_macro":
            overall_f1_macro,

        "overall_precision_weighted":
            overall_precision_weighted,

        "overall_recall_weighted":
            overall_recall_weighted,

        "overall_f1_weighted":
            overall_f1_weighted,

        # Metrics among samples where a rule fired
        "covered_accuracy":
            covered_accuracy,

        "covered_precision_macro":
            covered_precision_macro,

        "covered_recall_macro":
            covered_recall_macro,

        "covered_f1_macro":
            covered_f1_macro,

        "covered_precision_weighted":
            covered_precision_weighted,

        "covered_recall_weighted":
            covered_recall_weighted,

        "covered_f1_weighted":
            covered_f1_weighted,
    }

    # PER-CLASS METRICS
    per_class = []

    for label in labels:

        tp = sum(
            1
            for truth, pred in zip(
                y_true,
                y_pred
            )
            if truth == label
            and pred == label
        )

        fp = sum(
            1
            for truth, pred in zip(
                y_true,
                y_pred
            )
            if truth != label
            and pred == label
        )

        fn = sum(
            1
            for truth, pred in zip(
                y_true,
                y_pred
            )
            if truth == label
            and pred != label
        )

        support = sum(
            1
            for truth in y_true
            if truth == label
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp) > 0
            else 0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn) > 0
            else 0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        per_class.append(
            {
                "label": label,

                "support": support,

                "tp": int(tp),

                "fp": int(fp),

                "fn": int(fn),

                "precision": precision,

                "recall": recall,

                "f1": f1,
            }
        )

    # CONFUSION MATRIX
    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels + ["unknown"]
    )
    
    # FINAL RULE STATISTICS

    final_rule_stats = []

    for rule_id, data in (
        rule_statistics.items()
    ):

        matched = data["matched"]

        winning = (
            data["winning_predictions"]
        )

        tp = data["true_positive"]

        fp = data["false_positive"]

        # Rule precision:
        # among the times this rule actually won,
        # how often was it correct?
        rule_precision = (
            tp / winning
            if winning > 0
            else 0
        )

        # Rule recall:
        # among all actual examples of the rule's disease,
        # how many did this rule correctly classify?
        total_true_for_class = sum(
            1
            for truth in y_true
            if truth == data["label"]
        )

        rule_recall = (
            tp / total_true_for_class
            if total_true_for_class > 0
            else 0
        )

        rule_f1 = (
            2
            * rule_precision
            * rule_recall
            / (
                rule_precision
                + rule_recall
            )
            if (
                rule_precision
                + rule_recall
            ) > 0
            else 0
        )

        final_rule_stats.append(
            {
                "rule_id":
                    rule_id,

                "rule_name":
                    data["rule_name"],

                "label":
                    data["label"],

                "description":
                    data["description"],

                "priority":
                    data["priority"],

                "pattern":
                    data["pattern"],

                "matched":
                    matched,

                "winning_predictions":
                    winning,

                "true_positive":
                    tp,

                "false_positive":
                    fp,

                "precision":
                    rule_precision,

                "recall":
                    rule_recall,

                "f1":
                    rule_f1,

                "coverage":
                    (
                        matched / total
                        if total > 0
                        else 0
                    ),

                "examples_true_positive":
                    data[
                        "examples_true_positive"
                    ],

                "examples_false_positive":
                    data[
                        "examples_false_positive"
                    ],
            }
        )

    final_rule_stats.sort(
        key=lambda x: (
            x["precision"],
            x["coverage"]
        ),
        reverse=True,
    )

    return (
        metrics,
        cm,
        per_class,
        final_rule_stats,
        predictions,
    )


# RULE QUALITY


def analyze_rule_quality(
    rule_stats
):
    """
    Assign a simple quality score to each rule.
    """

    analysis = []

    for rule in rule_stats:

        score = 100

        suggestions = []

        if rule["precision"] < 0.50:

            score -= 35

            suggestions.append(
                "Precision is very low. "
                "Rule is likely too generic."
            )

        elif rule["precision"] < 0.70:

            score -= 20

            suggestions.append(
                "Increase specificity to "
                "reduce false positives."
            )

        if rule["recall"] < 0.40:

            score -= 20

            suggestions.append(
                "Recall is low. Rule misses "
                "many true examples."
            )

        if rule["coverage"] < 0.05:

            score -= 10

            suggestions.append(
                "Rule rarely activates."
            )

        elif rule["coverage"] > 0.60:

            score -= 15

            suggestions.append(
                "Rule activates too frequently."
            )

        if (
            rule["false_positive"]
            > rule["true_positive"]
        ):

            score -= 25

            suggestions.append(
                "Produces more false positives "
                "than true positives."
            )

        if rule["false_positive"] > 5:

            score -= 15

            suggestions.append(
                "Large number of false positives."
            )

        score = max(
            score,
            0
        )

        if score >= 90:

            quality = "Excellent"

        elif score >= 75:

            quality = "Good"

        elif score >= 60:

            quality = "Fair"

        else:

            quality = "Poor"

        if not suggestions:

            suggestions.append(
                "Rule looks stable."
            )

        analysis.append(
            {
                "rule_id":
                    rule["rule_id"],

                "rule_name":
                    rule["rule_name"],

                "label":
                    rule["label"],

                "quality":
                    quality,

                "quality_score":
                    score,

                "suggestions":
                    " ".join(
                        suggestions
                    ),
            }
        )

    return analysis

# WEAK / STRONG RULES

def detect_weak_rules(
    rule_stats
):

    weak = [
        r
        for r in rule_stats
        if (
            r["precision"] < 0.70
            or r["false_positive"]
            > r["true_positive"]
            or r["coverage"] > 0.60
        )
    ]

    weak.sort(
        key=lambda x: x["precision"]
    )

    return weak


def detect_strong_rules(
    rule_stats
):

    strong = [
        r
        for r in rule_stats
        if (
            r["precision"] >= 0.90
            and r["coverage"] >= 0.05
        )
    ]

    strong.sort(
        key=lambda x: x["precision"],
        reverse=True,
    )

    return strong

# ERROR ANALYSIS
def analyze_errors(
    predictions
):

    errors = []

    for prediction in predictions:

        if prediction["predicted_label"] == "unknown":

            errors.append(
                {
                    "text":
                        prediction["text"],

                    "true_label":
                        prediction["true_label"],

                    "predicted_label":
                        "unknown",

                    "rule":
                        None,

                    "rule_name":
                        None,

                    "error_type":
                        "no_rule_fired",
                }
            )

        elif (
            prediction["true_label"]
            != prediction["predicted_label"]
        ):

            errors.append(
                {
                    "text":
                        prediction["text"],

                    "true_label":
                        prediction["true_label"],

                    "predicted_label":
                        prediction[
                            "predicted_label"
                        ],

                    "rule":
                        prediction[
                            "winning_rule_id"
                        ],

                    "rule_name":
                        prediction[
                            "winning_rule_name"
                        ],

                    "error_type":
                        "false_positive",
                }
            )

    return errors


# IMPROVEMENT SUGGESTIONS

def build_improvement_suggestions(
    rule_stats
):

    suggestions = []

    for rule in rule_stats:

        text = []

        if rule["precision"] < 0.60:

            text.append(
                "Require additional symptoms "
                "before firing."
            )

        if rule["coverage"] > 0.50:

            text.append(
                "Current rule may be too broad."
            )

        if rule["recall"] < 0.50:

            text.append(
                "Consider adding alternative "
                "symptom patterns."
            )

        if (
            rule["false_positive"]
            > rule["true_positive"]
        ):

            text.append(
                "Inspect false-positive examples "
                "and refine the regex."
            )

        if not text:

            text.append(
                "Rule looks stable."
            )

        suggestions.append(
            {
                "rule_id":
                    rule["rule_id"],

                "rule_name":
                    rule["rule_name"],

                "recommendation":
                    " ".join(text),
            }
        )

    return suggestions


# SAVE PREDICTIONS

def save_predictions(
    predictions,
    output_dir,
    dataset_name
):

    path = (
        output_dir
        / f"predictions_{dataset_name}.csv"
    )

    rows = []

    for prediction in predictions:

        rows.append(
            {
                "dataset":
                    prediction["dataset"],

                "text":
                    prediction["text"],

                "true_label":
                    prediction["true_label"],

                "predicted_label":
                    prediction["predicted_label"],

                "correct":
                    prediction["correct"],

                "winning_rule_id":
                    prediction[
                        "winning_rule_id"
                    ],

                "winning_rule_name":
                    prediction[
                        "winning_rule_name"
                    ],

                "all_fired_rules":
                    "; ".join(
                        prediction[
                            "all_fired_rules"
                        ]
                    ),
            }
        )

    pd.DataFrame(rows).to_csv(
        path,
        index=False,
    )


# GENERATE HTML RULE INSPECTION REPORT


def generate_rule_html_report(
    all_rule_results,
    output_dir,
):
    """
    Generate an HTML page specifically designed for
    inspecting rules together with true-positive and
    false-positive examples.

    """

    output_dir = Path(
        output_dir
    )

    html_path = (
        output_dir
        / "rule_inspection.html"
    )

    page = []

    page.append(
        """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>RuleChef Rule Inspection</title>

<style>

body {
    font-family: Arial, sans-serif;
    margin: 30px;
    background: #f5f5f5;
    color: #222;
}

h1 {
    margin-bottom: 5px;
}

.subtitle {
    color: #666;
    margin-bottom: 25px;
}

.rule {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.rule-header {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.rule-name {
    font-size: 21px;
    font-weight: bold;
}

.label {
    font-weight: bold;
}

.pattern {
    background: #f0f0f0;
    padding: 12px;
    border-radius: 6px;
    font-family: monospace;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.metrics {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 15px 0;
}

.metric {
    background: #eeeeee;
    padding: 8px 12px;
    border-radius: 6px;
}

.section {
    margin-top: 20px;
}

.example {
    padding: 12px;
    margin: 8px 0;
    border-radius: 6px;
}

.tp {
    background: #e9f7ef;
    border-left: 5px solid #27ae60;
}

.fp {
    background: #fdecea;
    border-left: 5px solid #e74c3c;
}

.example-label {
    font-weight: bold;
    margin-bottom: 5px;
}

.example-text {
    line-height: 1.5;
}

table {
    border-collapse: collapse;
    width: 100%;
    background: white;
    margin-top: 15px;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

th {
    background: #eeeeee;
}

.good {
    color: #16803c;
    font-weight: bold;
}

.bad {
    color: #c0392b;
    font-weight: bold;
}

details {
    margin-top: 15px;
}

summary {
    cursor: pointer;
    font-weight: bold;
}

</style>

</head>

<body>

<h1>RuleChef Rule Inspection</h1>

<div class="subtitle">
Rules, performance, true positives and false positives
</div>
"""
    )

    
    # Summary table
   

    page.append(
        "<h2>Rule Summary</h2>"
    )

    page.append(
        """
<table>
<tr>
<th>Dataset</th>
<th>Rule</th>
<th>Class</th>
<th>Priority</th>
<th>Matched</th>
<th>Winning</th>
<th>TP</th>
<th>FP</th>
<th>Precision</th>
<th>Recall</th>
<th>F1</th>
</tr>
"""
    )

    for dataset_name, results in all_rule_results.items():

        for rule in results:

            precision_class = (
                "good"
                if rule["precision"] >= 0.90
                else "bad"
                if rule["precision"] < 0.70
                else ""
            )

            page.append(
                f"""
<tr>
<td>{html.escape(dataset_name)}</td>
<td>{html.escape(str(rule["rule_name"]))}</td>
<td>{html.escape(str(rule["label"]))}</td>
<td>{html.escape(str(rule["priority"]))}</td>
<td>{rule["matched"]}</td>
<td>{rule["winning_predictions"]}</td>
<td>{rule["true_positive"]}</td>
<td>{rule["false_positive"]}</td>
<td class="{precision_class}">
{rule["precision"]:.3f}
</td>
<td>{rule["recall"]:.3f}</td>
<td>{rule["f1"]:.3f}</td>
</tr>
"""
            )

    page.append(
        "</table>"
    )

    
    # Detailed rule cards
    

    page.append(
        "<h2>Detailed Rule Inspection</h2>"
    )

    for dataset_name, results in all_rule_results.items():

        page.append(
            f"<h2>{html.escape(dataset_name.title())} Set</h2>"
        )

        for rule in results:

            page.append(
                '<div class="rule">'
            )

            page.append(
                '<div class="rule-header">'
            )

            page.append(
                f"""
<div>
<div class="rule-name">
{html.escape(str(rule["rule_name"]))}
</div>

<div>
Class:
<span class="label">
{html.escape(str(rule["label"]))}
</span>
</div>

<div>
Rule ID:
{html.escape(str(rule["rule_id"]))}
</div>

<div>
Priority:
{html.escape(str(rule["priority"]))}
</div>
</div>
"""
            )

            page.append(
                "</div>"
            )

            # Pattern
            page.append(
                "<div class='section'>"
                "<strong>Rule pattern:</strong>"
                "</div>"
            )

            page.append(
                f"""
<div class="pattern">
{html.escape(str(rule["pattern"]))}
</div>
"""
            )

            # Description
            if rule.get("description"):

                page.append(
                    f"""
<div class="section">
<strong>Description:</strong>
<p>
{html.escape(str(rule["description"]))}
</p>
</div>
"""
                )

            # Metrics
            page.append(
                f"""
<div class="metrics">

<div class="metric">
Matched: {rule["matched"]}
</div>

<div class="metric">
Winning predictions: {rule["winning_predictions"]}
</div>

<div class="metric">
True positives: {rule["true_positive"]}
</div>

<div class="metric">
False positives: {rule["false_positive"]}
</div>

<div class="metric">
Precision: {rule["precision"]:.3f}
</div>

<div class="metric">
Recall: {rule["recall"]:.3f}
</div>

<div class="metric">
F1: {rule["f1"]:.3f}
</div>

</div>
"""
            )

            # True positives
            page.append(
                """
<div class="section">
<strong>
True-positive examples
</strong>
"""
            )

            tp_examples = rule[
                "examples_true_positive"
            ]

            if tp_examples:

                for example in tp_examples:

                    page.append(
                        f"""
<div class="example tp">

<div class="example-label">
TRUE POSITIVE
</div>

<div class="example-text">
{html.escape(example["text"])}
</div>

<div>
True:
{html.escape(example["true"])}
&nbsp;&nbsp;|
&nbsp;&nbsp;
Predicted:
{html.escape(example["predicted"])}
</div>

</div>
"""
                    )

            else:

                page.append(
                    "<p>No true-positive examples.</p>"
                )

            page.append(
                "</div>"
            )

            # False positives
            page.append(
                """
<div class="section">
<strong>
False-positive examples
</strong>
"""
            )

            fp_examples = rule[
                "examples_false_positive"
            ]

            if fp_examples:

                for example in fp_examples:

                    page.append(
                        f"""
<div class="example fp">

<div class="example-label">
FALSE POSITIVE
</div>

<div class="example-text">
{html.escape(example["text"])}
</div>

<div>
True:
{html.escape(example["true"])}
&nbsp;&nbsp;|
&nbsp;&nbsp;
Predicted:
{html.escape(example["predicted"])}
</div>

</div>
"""
                    )

            else:

                page.append(
                    "<p>No false-positive examples.</p>"
                )

            page.append(
                "</div>"
            )

            page.append(
                "</div>"
            )

    page.append(
        """
</body>
</html>
"""
    )

    with open(
        html_path,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "\n".join(page)
        )

    print(
        f"\nRule inspection HTML saved to:"
        f"\n{html_path}"
    )



# GENERATE REPORTS


def generate_reports(
    metrics,
    cm,
    per_class,
    rule_stats,
    predictions,
    labels,
    output_dir,
    dataset_name,
):
    """
    Generate reports for one dataset split.
    """

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    quality = analyze_rule_quality(
        rule_stats
    )

    weak_rules = detect_weak_rules(
        rule_stats
    )

    strong_rules = detect_strong_rules(
        rule_stats
    )

    errors = analyze_errors(
        predictions
    )

    suggestions = (
        build_improvement_suggestions(
            rule_stats
        )
    )

   
    # JSON report
   

    report_json = {

        "timestamp":
            datetime.now().isoformat(),

        "dataset":
            dataset_name,

        "labels":
            labels,

        "metrics":
            metrics,

        "confusion_matrix":
            cm.tolist()
            if cm is not None
            else [],

        "per_class":
            per_class,

        "rule_statistics":
            rule_stats,

        "rule_quality":
            quality,

        "rule_suggestions":
            suggestions,

        "weak_rules":
            weak_rules,

        "strong_rules":
            strong_rules,

        "misclassifications":
            errors,
    }

    with open(
        output_dir / f"report_{dataset_name}.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report_json,
            f,
            indent=2,
        )

    # Per-class CSV
    

    pd.DataFrame(
        per_class
    ).to_csv(
        output_dir
        / f"per_class_{dataset_name}.csv",
        index=False,
    )

    
    # Rule stats CSV
    

    rule_stats_csv = []

    for rule in rule_stats:

        row = {
            key: value
            for key, value in rule.items()
            if key not in [
                "examples_true_positive",
                "examples_false_positive",
            ]
        }

        rule_stats_csv.append(
            row
        )

    pd.DataFrame(
        rule_stats_csv
    ).to_csv(
        output_dir
        / f"rule_stats_{dataset_name}.csv",
        index=False,
    )

    
    # Rule quality
    

    pd.DataFrame(
        quality
    ).to_csv(
        output_dir
        / f"rule_quality_{dataset_name}.csv",
        index=False,
    )

   
    # Suggestions
   

    pd.DataFrame(
        suggestions
    ).to_csv(
        output_dir
        / f"rule_suggestions_{dataset_name}.csv",
        index=False,
    )

   
    # Weak rules
  

    weak_csv = []

    for rule in weak_rules:

        weak_csv.append(
            {
                key: value
                for key, value in rule.items()
                if key not in [
                    "examples_true_positive",
                    "examples_false_positive",
                ]
            }
        )

    pd.DataFrame(
        weak_csv
    ).to_csv(
        output_dir
        / f"weak_rules_{dataset_name}.csv",
        index=False,
    )

    # Strong rules
    strong_csv = []

    for rule in strong_rules:

        strong_csv.append(
            {
                key: value
                for key, value in rule.items()
                if key not in [
                    "examples_true_positive",
                    "examples_false_positive",
                ]
            }
        )

    pd.DataFrame(
        strong_csv
    ).to_csv(
        output_dir
        / f"strong_rules_{dataset_name}.csv",
        index=False,
    )

    # Misclassified examples
    
    pd.DataFrame(
        errors
    ).to_csv(
        output_dir
        / f"misclassified_{dataset_name}.csv",
        index=False,
    )

    # Rule examples

    example_rows = []

    for rule in rule_stats:

        for example in rule[
            "examples_true_positive"
        ]:

            example_rows.append(
                {
                    "dataset":
                        dataset_name,

                    "rule_id":
                        rule["rule_id"],

                    "rule_name":
                        rule["rule_name"],

                    "rule_label":
                        rule["label"],

                    "type":
                        "true_positive",

                    "example":
                        example["text"],

                    "true":
                        example["true"],

                    "predicted":
                        example["predicted"],
                }
            )

        for example in rule[
            "examples_false_positive"
        ]:

            example_rows.append(
                {
                    "dataset":
                        dataset_name,

                    "rule_id":
                        rule["rule_id"],

                    "rule_name":
                        rule["rule_name"],

                    "rule_label":
                        rule["label"],

                    "type":
                        "false_positive",

                    "example":
                        example["text"],

                    "true":
                        example["true"],

                    "predicted":
                        example["predicted"],
                }
            )

    pd.DataFrame(
        example_rows
    ).to_csv(
        output_dir
        / f"rule_examples_{dataset_name}.csv",
        index=False,
    )

    # Confusion matrix

    cm_labels = labels + ["unknown"]

    pd.DataFrame(
        cm,
        index=cm_labels,
        columns=cm_labels,
    ).to_csv(
        output_dir
        / f"confusion_matrix_{dataset_name}.csv"
    )
    # Markdown report
    md = []

    md.append(
        "# RuleChef Benchmark Report"
    )

    md.append(
        f"\nDataset split: **{dataset_name}**"
    )

    md.append(
        f"\nGenerated: {datetime.now()}"
    )

    md.append(
        "\n## Overall Metrics"
    )

    md.append(
        "\n| Metric | Value |"
    )

    md.append(
        "|---|---|"
    )

    for key, value in metrics.items():

        if isinstance(
            value,
            float
        ):

            md.append(
                f"| {key} | {value:.4f} |"
            )

        else:

            md.append(
                f"| {key} | {value} |"
            )

    # Per-class

    md.append(
        "\n## Per-Class Performance"
    )

    md.append(
        "\n| Class | Support | Precision | Recall | F1 |"
    )

    md.append(
        "|---|---:|---:|---:|---:|"
    )

    for row in per_class:

        md.append(
            f"| {row['label']} "
            f"| {row['support']} "
            f"| {row['precision']:.3f} "
            f"| {row['recall']:.3f} "
            f"| {row['f1']:.3f} |"
        )

    # Rules
   
    md.append(
        "\n## Rules"
    )

    md.append(
        "\n| Rule | Class | TP | FP | Precision | Recall | F1 |"
    )

    md.append(
        "|---|---|---:|---:|---:|---:|---:|"
    )

    for rule in rule_stats:

        md.append(
            f"| {rule['rule_name']} "
            f"| {rule['label']} "
            f"| {rule['true_positive']} "
            f"| {rule['false_positive']} "
            f"| {rule['precision']:.3f} "
            f"| {rule['recall']:.3f} "
            f"| {rule['f1']:.3f} |"
        )

   
    # False positives
    
    md.append(
        "\n## False-Positive Examples"
    )

    for rule in rule_stats:

        if not rule[
            "examples_false_positive"
        ]:

            continue

        md.append(
            f"\n### {rule['rule_name']}"
        )

        for example in rule[
            "examples_false_positive"
        ]:

            md.append(
                f"\n- **True:** "
                f"{example['true']}"
            )

            md.append(
                f"- **Predicted:** "
                f"{example['predicted']}"
            )

            md.append(
                f"- **Text:** "
                f"{example['text']}"
            )

    # True positives
   

    md.append(
        "\n## True-Positive Examples"
    )

    for rule in rule_stats:

        if not rule[
            "examples_true_positive"
        ]:

            continue

        md.append(
            f"\n### {rule['rule_name']}"
        )

        for example in rule[
            "examples_true_positive"
        ]:

            md.append(
                f"\n- **True:** "
                f"{example['true']}"
            )

            md.append(
                f"- **Predicted:** "
                f"{example['predicted']}"
            )

            md.append(
                f"- **Text:** "
                f"{example['text']}"
            )

    # Weak rules

    md.append(
        "\n## Weak Rules"
    )

    for rule in weak_rules:

        md.append(
            f"- {rule['rule_name']} "
            f"({rule['label']}): "
            f"precision={rule['precision']:.3f}, "
            f"recall={rule['recall']:.3f}, "
            f"FP={rule['false_positive']}"
        )

    # Suggestions

    md.append(
        "\n## Rule Improvement Suggestions"
    )

    for suggestion in suggestions:

        md.append(
            f"\n### {suggestion['rule_name']}"
        )

        md.append(
            f"- {suggestion['recommendation']}"
        )

    with open(
        output_dir
        / f"report_{dataset_name}.md",
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "\n".join(md)
        )


# COMBINED SUMMARY REPORT

def generate_combined_summary(
    all_metrics,
    all_per_class,
    labels,
    output_dir,
):
    """
    Create one summary comparing train, validation and test.
    """

    output_dir = Path(
        output_dir
    )

    # CSV summary


    rows = []

    for dataset_name, metrics in (
        all_metrics.items()
    ):

        rows.append(
            {
                "dataset":
                    dataset_name,

                "total_samples":
                    metrics["total_samples"],

                "covered_samples":
                    metrics["covered_samples"],

                "coverage":
                    metrics["coverage"],

                "overall_accuracy":
                    metrics["overall_accuracy"],

                "overall_precision_macro":
                    metrics[
                        "overall_precision_macro"
                    ],

                "overall_recall_macro":
                    metrics[
                        "overall_recall_macro"
                    ],

                "overall_f1_macro":
                    metrics[
                        "overall_f1_macro"
                    ],

                "covered_accuracy":
                    metrics[
                        "covered_accuracy"
                    ],

                "covered_precision_macro":
                    metrics[
                        "covered_precision_macro"
                    ],

                "covered_recall_macro":
                    metrics[
                        "covered_recall_macro"
                    ],

                "covered_f1_macro":
                    metrics[
                        "covered_f1_macro"
                    ],
            }
        )

    pd.DataFrame(
        rows
    ).to_csv(
        output_dir
        / "summary_train_val_test.csv",
        index=False,
    )

  
    # Markdown

    md = []

    md.append(
        "# RuleChef Multi-Class Benchmark Summary"
    )

    md.append(
        f"\nGenerated: {datetime.now()}"
    )

    md.append(
        "\n## Selected Classes"
    )

    for label in labels:

        md.append(
            f"- {label}"
        )

    md.append(
        "\n## Train / Validation / Test Performance"
    )

    md.append(
        """
| Dataset | Samples | Coverage | Overall Accuracy | Overall Macro Precision | Overall Macro Recall | Overall Macro F1 |
|---|---:|---:|---:|---:|---:|---:|
"""
    )

    for dataset_name, metrics in (
        all_metrics.items()
    ):

        md.append(
            f"| {dataset_name} "
            f"| {metrics['total_samples']} "
            f"| {metrics['coverage']:.3f} "
            f"| {metrics['overall_accuracy']:.3f} "
            f"| {metrics['overall_precision_macro']:.3f} "
            f"| {metrics['overall_recall_macro']:.3f} "
            f"| {metrics['overall_f1_macro']:.3f} |"
        )
    # Per-class comparison

    md.append(
        "\n## Per-Class Performance"
    )

    for dataset_name, class_rows in (
        all_per_class.items()
    ):

        md.append(
            f"\n### {dataset_name.title()} Set"
        )

        md.append(
            "\n| Class | Support | Precision | Recall | F1 |"
        )

        md.append(
            "|---|---:|---:|---:|---:|"
        )

        for row in class_rows:

            md.append(
                f"| {row['label']} "
                f"| {row['support']} "
                f"| {row['precision']:.3f} "
                f"| {row['recall']:.3f} "
                f"| {row['f1']:.3f} |"
            )

    with open(
        output_dir
        / "summary_train_val_test.md",
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "\n".join(md)
        )

# MAIN

def main():

    print(
        "\n"
        + "=" * 80
    )

    print(
        "RuleChef 5-Class Benchmark"
    )

    print(
        "=" * 80
    )

    # Prepare directories

    if os.path.exists(
        STORAGE_PATH
    ):

        print(
            f"\nRemoving previous RuleChef storage:"
            f" {STORAGE_PATH}"
        )

        shutil.rmtree(
            STORAGE_PATH
        )

    RULES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Load dataset

    (
        train_df,
        val_df,
        test_df,
        selected_diseases,
    ) = load_data(
        DATASET_PATH,
        selected_diseases=SELECTED_DISEASES,
        number_of_classes=NUMBER_OF_CLASSES,
        test_size=TEST_SIZE,
        val_size=VALIDATION_FROM_TEMP,
        random_state=RANDOM_STATE,
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "SELECTED DISEASE CLASSES"
    )

    print(
        "=" * 80
    )

    for i, disease in enumerate(
        selected_diseases,
        1
    ):

        print(
            f"{i}. {disease}"
        )

    # CREATE RULECHEF TASK

    task = Task(
        name="Disease Classification",

        description=(
            "Classify a disease based on "
            "the symptoms described in the text."
        ),

        input_schema={
            "text": "str"
        },

        output_schema={
            "label": "str"
        },

        type=TaskType.CLASSIFICATION,

        text_field="text",
    )

   
    # GEMINI CLIENT
    

    client = GeminiClient(
        api_key=API_KEY
    )

    
    # RULECHEF
   

    chef = RuleChef(
        task,
        client,
        storage_path=STORAGE_PATH,
    )

   
    # RULE LEARNING
    
    #
    # IMPORTANT:
    #
    # Only TRAINING examples are used here.
    #
    # Validation and test data are NOT added to RuleChef.
    #
   

    print(
        "\n"
        + "=" * 80
    )

    print(
        "RULE LEARNING"
    )

    print(
        "=" * 80
    )

    
    # Make sure every class has enough training examples
  

    class_train_counts = (
        train_df["label"]
        .value_counts()
    )

    insufficient = [
        label
        for label in selected_diseases
        if class_train_counts.get(
            label,
            0
        ) < EXAMPLES_PER_CLASS
    ]

    if insufficient:

        raise ValueError(
            "Not enough training examples for "
            f"EXAMPLES_PER_CLASS={EXAMPLES_PER_CLASS}. "
            f"Insufficient classes: {insufficient}"
        )

    
    # Sample examples from each class
   

    rule_learning_df = (
        train_df
        .groupby(
            "label",
            group_keys=False
        )
        .sample(
            n=EXAMPLES_PER_CLASS,
            random_state=RANDOM_STATE,
        )
        .sort_values(
            "label"
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"\nUsing "
        f"{EXAMPLES_PER_CLASS} training examples "
        f"per class for rule learning."
    )

    print(
        f"Total rule-learning examples: "
        f"{len(rule_learning_df)}"
    )

    
    #
    # 15 examples/class:
    # Batch 1 = examples 1-5
    # Batch 2 = examples 6-10
    # Batch 3 = examples 11-15
   

    batches = []

    for start in [
        0,
        5,
        10,
    ]:

        batch = pd.concat(
            [
                group.iloc[
                    start:start + 5
                ]
                for _, group
                in rule_learning_df.groupby(
                    "label"
                )
            ]
        )

        batches.append(
            batch
        )

    client.set_mode(
        "synthesis"
    )

    learned_rules = None

    
    # Incremental rule learning
    

    for batch_number, batch in enumerate(
        batches,
        1
    ):

        print(
            "\n"
            + "-" * 80
        )

        print(
            f"BATCH {batch_number}"
        )

        print(
            "-" * 80
        )

        for _, row in batch.iterrows():

            if (
                pd.isna(row["text"])
                or pd.isna(row["label"])
            ):

                continue

            chef.add_example(
                {
                    "text":
                        str(row["text"])
                },

                {
                    "label":
                        str(row["label"])
                },
            )

        start_time = time.time()

        rules = chef.learn_rules()

        elapsed = (
            time.time()
            - start_time
        )

        learned_rules = rules

        print(
            f"\nRule learning time: "
            f"{elapsed:.2f}s"
        )

        print(
            f"RuleChef result type: "
            f"{type(rules)}"
        )

       
        # Save raw RuleChef output
        

        raw_rules_path = (
            RULES_DIR
            / f"batch_{batch_number}_rules.txt"
        )

        with open(
            raw_rules_path,
            "w",
            encoding="utf-8",
        ) as f:

            f.write(
                str(rules)
            )

        print(
            f"Saved raw rules to: "
            f"{raw_rules_path}"
        )

   
    # EXTRACT FINAL RULES
    
    print(
        "\n"
        + "=" * 80
    )

    print(
        "EXTRACTING FINAL RULES"
    )

    print(
        "=" * 80
    )

    rules_list = (
        extract_rules_from_rulechef(
            learned_rules
        )
    )

    if not rules_list:

        raise ValueError(
            "No rules were extracted from RuleChef."
        )

    
    # Save final rules
    

    rules_json_path = (
        RULES_DIR
        / "final_rules.json"
    )

    with open(
        rules_json_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            {
                "classes":
                    selected_diseases,

                "rules":
                    rules_list,
            },
            f,
            indent=2,
        )

    print(
        f"\nSaved "
        f"{len(rules_list)} rules to:"
    )

    print(
        rules_json_path
    )

    
    # PRINT RULES FOR QUICK INSPECTION
    

    print(
        "\n"
        + "=" * 80
    )

    print(
        "LEARNED RULES"
    )

    print(
        "=" * 80
    )

    for i, rule in enumerate(
        rules_list,
        1
    ):

        print(
            f"\nRule {i}"
        )

        print(
            f"ID:       {rule['id']}"
        )

        print(
            f"Name:     {rule['name']}"
        )

        print(
            f"Class:    {rule['label']}"
        )

        print(
            f"Priority: {rule['priority']}"
        )

        print(
            f"Pattern:  {rule['pattern']}"
        )

        if rule["description"]:

            print(
                f"Description: "
                f"{rule['description']}"
            )

    
    # LOAD RULE ENGINE
    

    engine = RuleEngine(
        rules_json_path
    )

    print(
        f"\nLoaded "
        f"{len(engine.rules)} executable rules."
    )

   
    # EVALUATE TRAIN / VALIDATION / TEST
    

    datasets = {
        "train":
            train_df,

        "validation":
            val_df,

        "test":
            test_df,
    }

    all_metrics = {}

    all_per_class = {}

    all_rule_results = {}

    all_predictions = {}

    
    # Evaluate each split
   

    for dataset_name, dataset_df in (
        datasets.items()
    ):

        print(
            "\n"
            + "=" * 80
        )

        print(
            f"EVALUATING {dataset_name.upper()} SET"
        )

        print(
            "=" * 80
        )

        (
            metrics,
            cm,
            per_class,
            rule_stats,
            predictions,
        ) = evaluate(
            engine,
            dataset_df,
            selected_diseases,
            dataset_name=dataset_name,
            max_examples_per_rule=10,
        )

        all_metrics[
            dataset_name
        ] = metrics

        all_per_class[
            dataset_name
        ] = per_class

        all_rule_results[
            dataset_name
        ] = rule_stats

        all_predictions[
            dataset_name
        ] = predictions

        
        # Print metrics
        

        print(
            f"\nSamples: "
            f"{metrics['total_samples']}"
        )

        print(
            f"Covered by rules: "
            f"{metrics['covered_samples']} "
            f"/ "
            f"{metrics['total_samples']}"
        )

        print(
            f"Coverage: "
            f"{metrics['coverage']:.2%}"
        )

        print(
            f"\nOverall Accuracy: "
            f"{metrics['overall_accuracy']:.4f}"
        )

        print(
            f"Overall Macro Precision: "
            f"{metrics['overall_precision_macro']:.4f}"
        )

        print(
            f"Overall Macro Recall: "
            f"{metrics['overall_recall_macro']:.4f}"
        )

        print(
            f"Overall Macro F1: "
            f"{metrics['overall_f1_macro']:.4f}"
        )

        if (
            metrics["covered_accuracy"]
            is not None
        ):

            print(
                "\nMetrics on samples where "
                "a rule fired:"
            )

            print(
                f"Covered Accuracy: "
                f"{metrics['covered_accuracy']:.4f}"
            )

            print(
                f"Covered Macro Precision: "
                f"{metrics['covered_precision_macro']:.4f}"
            )

            print(
                f"Covered Macro Recall: "
                f"{metrics['covered_recall_macro']:.4f}"
            )

            print(
                f"Covered Macro F1: "
                f"{metrics['covered_f1_macro']:.4f}"
            )

        # Per-class output
       

        print(
            "\nPer-class performance:"
        )

        for row in per_class:

            print(
                f"  {row['label']}: "
                f"precision={row['precision']:.3f}, "
                f"recall={row['recall']:.3f}, "
                f"F1={row['f1']:.3f}, "
                f"support={row['support']}"
            )

        # Generate reports for this split
       

        generate_reports(
            metrics,
            cm,
            per_class,
            rule_stats,
            predictions,
            selected_diseases,
            REPORTS_DIR,
            dataset_name,
        )

        save_predictions(
            predictions,
            REPORTS_DIR,
            dataset_name,
        )

    # COMBINED SUMMARY
    

    generate_combined_summary(
        all_metrics,
        all_per_class,
        selected_diseases,
        REPORTS_DIR,
    )
    # RULE INSPECTION HTML

    generate_rule_html_report(
        all_rule_results,
        REPORTS_DIR,
    )

    # SAVE ALL RESULTS TO JSON

    combined_results = {

        "timestamp":
            datetime.now().isoformat(),

        "classes":
            selected_diseases,

        "metrics":
            all_metrics,

        "per_class":
            all_per_class,

        "rules_by_dataset":
            all_rule_results,
    }

    with open(
        REPORTS_DIR
        / "complete_benchmark.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            combined_results,
            f,
            indent=2,
        )

   
    # FINAL OUTPUT
   

    print(
        "\n"
        + "=" * 80
    )

    print(
        "BENCHMARK COMPLETED"
    )

    print(
        "=" * 80
    )

    print(
        "\nSelected classes:"
    )

    for disease in selected_diseases:

        print(
            f"  - {disease}"
        )

    print(
        "\nGenerated files:"
    )

    print(
        f"  {RULES_DIR / 'final_rules.json'}"
    )

    print(
        f"  {REPORTS_DIR / 'rule_inspection.html'}"
    )

    print(
        f"  {REPORTS_DIR / 'summary_train_val_test.md'}"
    )

    print(
        f"  {REPORTS_DIR / 'summary_train_val_test.csv'}"
    )

    print(
        f"  {REPORTS_DIR / 'complete_benchmark.json'}"
    )

    print(
        f"  {REPORTS_DIR / 'predictions_train.csv'}"
    )

    print(
        f"  {REPORTS_DIR / 'predictions_validation.csv'}"
    )

    print(
        f"  {REPORTS_DIR / 'predictions_test.csv'}"
    )

    print(
        "\nYou can open this file in a browser "
        "to inspect every rule and its examples:"
    )

    print(
        f"  {REPORTS_DIR / 'rule_inspection.html'}"
    )

    print(
        "\n"
        + "=" * 80
    )

# ENTRY POINT


if __name__ == "__main__":
    main()

