"""
benchmark.py – Rule‑based classification benchmark
Inspired by GermanLER, designed for text classification with regex rules.
"""

import json
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)
import time
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------------------
# 1. DATASET LOADER (reproduces your original split)
# ----------------------------------------------------------------------
def load_data(csv_path, selected_diseases=None, test_size=0.3, val_size=0.5, random_state=42):
    df = pd.read_csv(csv_path)
    df["label"] = df["label"].str.lower().str.strip()
    df["text"] = df["text"].str.lower().str.strip()

    if selected_diseases is None:
        # take top 2 most frequent (as in your experiment)
        top2 = df["label"].value_counts().head(2).index.tolist()
        selected_diseases = top2

    df_binary = df[df["label"].isin(selected_diseases)].copy()

    # train / temp (val+test)
    train_df, temp_df = train_test_split(
        df_binary,
        test_size=test_size,
        stratify=df_binary["label"],
        random_state=random_state
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=val_size,
        stratify=temp_df["label"],
        random_state=random_state
    )

    return train_df, val_df, test_df, selected_diseases

# ----------------------------------------------------------------------
# 2. RULE ENGINE (lightweight, no RuleChef dependency)
# ----------------------------------------------------------------------
class RuleEngine:
    def __init__(self, rules_json_path):
        with open(rules_json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON file: {e}")

        # Extract the rules list
        if isinstance(data, dict) and "rules" in data:
            rules = data["rules"]
        elif isinstance(data, list):
            rules = data
        else:
            raise TypeError(
                f"Rules file must contain a list of rules or a dict with a 'rules' key. "
                f"Got {type(data)} instead."
            )

        self.rules = []
        for idx, r in enumerate(rules):
            if not isinstance(r, dict):
                raise TypeError(f"Rule at index {idx} is not a dict, got {type(r)}: {r!r}")

            # Try to get the regex pattern (use 'content' if present, else 'pattern')
            pattern_str = r.get("content") or r.get("pattern")
            if not pattern_str:
                raise KeyError(f"Rule {idx} missing 'content' or 'pattern' key")

            # Try to get the label from output_template.label, or fallback to direct 'label'
            if "output_template" in r and isinstance(r["output_template"], dict):
                label = r["output_template"].get("label")
            else:
                label = r.get("label")

            if not label:
                raise KeyError(f"Rule {idx} missing label (either in output_template.label or direct 'label')")

            pattern = re.compile(pattern_str, re.IGNORECASE)
            self.rules.append({
                "id": r.get("id", f"rule_{idx}"),
                "name": r.get("name", "Unnamed"),
                "label": label,
                "priority": r.get("priority", 0),
                "pattern": pattern
            })

        # Sort by priority descending (higher first)
        self.rules.sort(key=lambda x: x["priority"], reverse=True)

    def predict(self, text):
        """Return predicted label or None if no rule matches."""
        for rule in self.rules:
            if rule["pattern"].search(text):
                return rule["label"]
        return None

# ----------------------------------------------------------------------
# 3. EVALUATION
# ----------------------------------------------------------------------
def evaluate(engine, test_df, labels):
    y_true = []
    y_pred = []
    predictions = []   # for per-rule stats

    for _, row in test_df.iterrows():
        text = row["text"]
        true_label = row["label"]
        y_true.append(true_label)

        pred_label = engine.predict(text)
        y_pred.append(pred_label if pred_label is not None else "unknown")

        predictions.append({
            "text": text,
            "true_label": true_label,
            "pred_label": pred_label
        })

    # ------------------------------------------------------------------
    # 3a. Overall metrics (including unknowns)
    # ------------------------------------------------------------------
    known_mask = [p != "unknown" for p in y_pred]
    covered = sum(known_mask)
    total = len(y_pred)
    coverage = covered / total if total > 0 else 0.0

    y_true_known = [t for t, p in zip(y_true, y_pred) if p != "unknown"]
    y_pred_known = [p for p in y_pred if p != "unknown"]

    if len(y_true_known) == 0:
        metrics = {
            "coverage": coverage,
            "covered_samples": covered,
            "total_samples": total,
            "accuracy": None,
            "precision_macro": None,
            "recall_macro": None,
            "f1_macro": None,
            "precision_micro": None,
            "recall_micro": None,
            "f1_micro": None,
            "precision_weighted": None,
            "recall_weighted": None,
            "f1_weighted": None,
        }
        cm = None
        per_class = []
        rule_stats = []
        return metrics, cm, per_class, rule_stats, predictions

    acc = accuracy_score(y_true_known, y_pred_known)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="macro", zero_division=0
    )
    prec_micro, rec_micro, f1_micro, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="micro", zero_division=0
    )
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true_known, y_pred_known, average="weighted", zero_division=0
    )

    metrics = {
        "coverage": coverage,
        "covered_samples": covered,
        "total_samples": total,
        "accuracy": acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "precision_micro": prec_micro,
        "recall_micro": rec_micro,
        "f1_micro": f1_micro,
        "precision_weighted": prec_weighted,
        "recall_weighted": rec_weighted,
        "f1_weighted": f1_weighted,
    }

    # ------------------------------------------------------------------
    # 3b. Confusion matrix
    # ------------------------------------------------------------------
    all_labels = sorted(set(y_true_known + y_pred_known))
    cm = confusion_matrix(y_true_known, y_pred_known, labels=all_labels)

    # ------------------------------------------------------------------
    # 3c. Per‑class metrics
    # ------------------------------------------------------------------
    per_class = []
    for label in all_labels:
        tp = np.sum((np.array(y_true_known) == label) & (np.array(y_pred_known) == label))
        fp = np.sum((np.array(y_true_known) != label) & (np.array(y_pred_known) == label))
        fn = np.sum((np.array(y_true_known) == label) & (np.array(y_pred_known) != label))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        per_class.append({
            "label": label,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "precision": prec,
            "recall": rec,
            "f1": f1
        })

    # ------------------------------------------------------------------
    # 3d. Per‑rule statistics
    # ------------------------------------------------------------------
    rule_stats = []
    for rule in engine.rules:
        matched = 0
        correct = 0
        for pred in predictions:
            if pred["pred_label"] is None:
                continue
            if rule["pattern"].search(pred["text"]):
                matched += 1
                if pred["pred_label"] == pred["true_label"]:
                    correct += 1
        precision = correct / matched if matched > 0 else 0.0
        rule_stats.append({
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "matched": matched,
            "correct": correct,
            "precision": precision
        })

    return metrics, cm, per_class, rule_stats, predictions

# ----------------------------------------------------------------------
# 4. REPORT GENERATION
# ----------------------------------------------------------------------
def generate_reports(metrics, cm, per_class, rule_stats, labels, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 4a. JSON report
    report_json = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "confusion_matrix": cm.tolist() if cm is not None else [],
        "per_class": per_class,
        "rule_stats": rule_stats,
        "labels": labels
    }
    with open(Path(output_dir) / "report.json", "w") as f:
        json.dump(report_json, f, indent=2)

    # 4b. Per‑class CSV
    df_class = pd.DataFrame(per_class)
    df_class.to_csv(Path(output_dir) / "per_class.csv", index=False)

    # 4c. Rule stats CSV
    df_rules = pd.DataFrame(rule_stats)
    df_rules.to_csv(Path(output_dir) / "rule_stats.csv", index=False)

    # 4d. Markdown report
    lines = []
    lines.append("# Rule‑Based Classification Benchmark Report\n")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("## Overall Metrics")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    for k, v in metrics.items():
        if v is not None:
            if isinstance(v, float):
                lines.append(f"| {k} | {v:.4f} |")
            else:
                lines.append(f"| {k} | {v} |")
        else:
            lines.append(f"| {k} | N/A |")

    lines.append("\n## Confusion Matrix")
    if cm is not None:
        labels = sorted(set([c["label"] for c in per_class]))
        header = "| " + " | ".join([""] + labels) + " |"
        sep = "| " + " | ".join(["---"] * (len(labels)+1)) + " |"
        lines.append(header)
        lines.append(sep)
        for i, row in enumerate(cm):
            row_str = f"| {labels[i]} | " + " | ".join(str(int(v)) for v in row) + " |"
            lines.append(row_str)
    else:
        lines.append("No predictions made.")

    lines.append("\n## Per‑Class Metrics")
    lines.append("| Label | TP | FP | FN | Precision | Recall | F1 |")
    lines.append("|-------|----|----|----|-----------|--------|----|")
    for c in per_class:
        lines.append(
            f"| {c['label']} | {c['tp']} | {c['fp']} | {c['fn']} | "
            f"{c['precision']:.4f} | {c['recall']:.4f} | {c['f1']:.4f} |"
        )

    lines.append("\n## Per‑Rule Statistics")
    lines.append("| Rule ID | Name | Matched | Correct | Precision |")
    lines.append("|---------|------|---------|---------|-----------|")
    for r in rule_stats:
        lines.append(
            f"| {r['rule_id']} | {r['rule_name']} | {r['matched']} | {r['correct']} | "
            f"{r['precision']:.4f} |"
        )

    with open(Path(output_dir) / "report.md", "w") as f:
        f.write("\n".join(lines))

    print(f"Reports saved to {output_dir}/")

# ----------------------------------------------------------------------
# 5. MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rule-based classification benchmark")
    parser.add_argument("--dataset", default="Symptom2Disease.csv", help="Path to CSV dataset")
    parser.add_argument("--rules", default="gemini_rules.json", help="Path to rules JSON")
    parser.add_argument("--output", default="./results", help="Output directory")
    parser.add_argument("--test-size", type=float, default=0.3, help="Test split fraction")
    parser.add_argument("--val-size", type=float, default=0.5, help="Validation split fraction within temp")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Load data
    train_df, val_df, test_df, labels = load_data(
        args.dataset,
        test_size=args.test_size,
        val_size=args.val_size,
        random_state=args.seed
    )
    print(f"Loaded dataset: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
    print(f"Selected diseases: {labels}")

    # Load rule engine
    engine = RuleEngine(args.rules)
    print(f"Loaded {len(engine.rules)} rules.")

    # Evaluate on test set
    start = time.time()
    metrics, cm, per_class, rule_stats, predictions = evaluate(engine, test_df, labels)
    elapsed = time.time() - start
    print(f"Evaluation completed in {elapsed:.2f}s")
    print(f"Coverage: {metrics['covered_samples']}/{metrics['total_samples']} ({metrics['coverage']:.2%})")
    if metrics['accuracy'] is not None:
        print(f"Accuracy (on known): {metrics['accuracy']:.4f}")

    # Generate reports
    generate_reports(metrics, cm, per_class, rule_stats, labels, args.output)