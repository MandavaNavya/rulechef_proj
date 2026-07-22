
import os
import shutil
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from google import genai
from rulechef import RuleChef, Task, TaskType


# CLEAN OLD RULECHEF STORAGE
storage_path = "./rulechef_binary"

if os.path.exists(storage_path):
    shutil.rmtree(storage_path)

# Directory for saving learned rules
rules_dir = "learned_rules"
os.makedirs(rules_dir, exist_ok=True)


# Gemini Client (Single Model)

class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.active_model = "gemini-2.5-flash"
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

            def create(self, model=None, messages=None, **kwargs):
                prompt = ""
                for m in messages:
                    prompt += f"{m.get('role','').upper()}: {m.get('content','')}\n"

                for attempt in range(3):
                    try:
                        response = self.parent.client.models.generate_content(
                            model=self.parent.active_model,
                            contents=prompt,
                        )

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

                    except Exception as e:
                        if attempt < 2:
                            time.sleep((attempt + 1) * 5)
                        else:
                            raise e


# Logging
output_log = []

def log(msg):
    print(msg)
    output_log.append(str(msg))


# Load Dataset
df = pd.read_csv("Symptom2Disease.csv")

df["label"] = df["label"].str.lower().str.strip()
df["text"] = df["text"].str.lower().str.strip()

log("\n=== Disease Distribution ===")
disease_counts = df["label"].value_counts()
log(disease_counts)

selected_diseases = disease_counts.head(2).index.tolist()
log("\n=== Selected Diseases ===")
log(selected_diseases)

df_binary = df[df["label"].isin(selected_diseases)].copy()


# Split
train_df, temp_df = train_test_split(
    df_binary,
    test_size=0.30,
    stratify=df_binary["label"],
    random_state=42
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    stratify=temp_df["label"],
    random_state=42
)


# RULE LEARNING SETUP
examples_per_class = 15

rule_learning_df = (
    train_df
    .groupby("label", group_keys=False)
    .sample(n=examples_per_class, random_state=42)
    .sort_values("label")
    .reset_index(drop=True)
)

batch1 = pd.concat([g.iloc[:5] for _, g in rule_learning_df.groupby("label")])
batch2 = pd.concat([g.iloc[5:10] for _, g in rule_learning_df.groupby("label")])
batch3 = pd.concat([g.iloc[10:15] for _, g in rule_learning_df.groupby("label")])

batches = [batch1, batch2, batch3]


# Task
task = Task(
    name="Disease Classification",
    description="Classify disease based on symptoms",
    input_schema={"text": "str"},
    output_schema={"label": "str"},
    type=TaskType.CLASSIFICATION,
    text_field="text",
)

client = GeminiClient(api_key=yourapikey)
chef = RuleChef(task, client, storage_path=storage_path)


results = []
all_rules = []


client.set_mode("synthesis")

for i, batch in enumerate(batches, 1):

    log(f"\n===== BATCH {i} =====")

    for _, row in batch.iterrows():
        if pd.isna(row["text"]) or pd.isna(row["label"]):
            continue
        chef.add_example({"text": str(row["text"])},
                         {"label": str(row["label"])})

    start = time.time()
    rules = chef.learn_rules()
    end = time.time()

    log(f"Rule learning time: {end-start:.2f}s")

    # SAVE RULES PER BATCH
    rule_file = os.path.join(rules_dir, f"batch_{i}_rules.txt")
    with open(rule_file, "w", encoding="utf-8") as f:
        f.write(str(rules))

    log(f"Saved rules to {rule_file}")

    all_rules.append((i, str(rules)))

    # VALIDATION
    client.set_mode("evaluation")

    y_true, y_pred = [], []

    for _, row in val_df.iterrows():
        pred = chef.extract({"text": row["text"]})

        label = pred.get("label") if isinstance(pred, dict) else None

        if label not in selected_diseases:
            label = "unknown"

        y_true.append(row["label"])
        y_pred.append(label)

    filtered = [(t, p) for t, p in zip(y_true, y_pred) if p != "unknown"]

    if len(filtered) == 0:
        log("⚠ No valid predictions found!")
        continue

    y_true_f, y_pred_f = zip(*filtered)

    acc = accuracy_score(y_true_f, y_pred_f)
    prec = precision_score(y_true_f, y_pred_f, average="macro", zero_division=0)
    rec = recall_score(y_true_f, y_pred_f, average="macro", zero_division=0)
    f1 = f1_score(y_true_f, y_pred_f, average="macro", zero_division=0)

    log(f"Validation Accuracy : {acc:.4f}")
    log(f"Validation Precision: {prec:.4f}")
    log(f"Validation Recall   : {rec:.4f}")
    log(f"Validation F1       : {f1:.4f}")

    results.append((i, acc, prec, rec, f1))

    client.set_mode("synthesis")


# FINAL TEST
log("\n===== FINAL TEST =====")

y_true, y_pred = [], []

for _, row in test_df.iterrows():
    pred = chef.extract({"text": row["text"]})
    label = pred.get("label") if isinstance(pred, dict) else None

    if label not in selected_diseases:
        label = "unknown"

    y_true.append(row["label"])
    y_pred.append(label)

filtered = [(t, p) for t, p in zip(y_true, y_pred) if p != "unknown"]
y_true_f, y_pred_f = zip(*filtered)

test_acc = accuracy_score(y_true_f, y_pred_f)
test_prec = precision_score(y_true_f, y_pred_f, average="macro", zero_division=0)
test_rec = recall_score(y_true_f, y_pred_f, average="macro", zero_division=0)
test_f1 = f1_score(y_true_f, y_pred_f, average="macro", zero_division=0)
cm = confusion_matrix(y_true_f, y_pred_f)

log(f"Test Accuracy : {test_acc:.4f}")
log(f"Test Precision: {test_prec:.4f}")
log(f"Test Recall   : {test_rec:.4f}")
log(f"Test F1       : {test_f1:.4f}")
log(f"Confusion Matrix:\n{cm}")


# SAVE FINAL RULES
final_rules_file = "final_learned_rules.txt"
with open(final_rules_file, "w", encoding="utf-8") as f:
    f.write(str(rules))

log(f"Saved final rules to {final_rules_file}")


# SAVE LOG
with open("incre_approch_rulechef_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_log))

print("\nSaved results log and rules.")