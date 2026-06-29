import pandas as pd
import time
from sklearn.model_selection import train_test_split
from google import genai
from rulechef import RuleChef, Task, TaskType


# =====================================================
# Gemini Client (Dual Model)
# =====================================================

class GeminiDualClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.synthesis_model = "gemini-2.5-flash"
        self.eval_model = "gemini-2.5-flash-lite"
        self.active_model = self.synthesis_model
        self.chat = self.Chat(self)

    def set_mode(self, mode="synthesis"):
        if mode == "evaluation":
            self.active_model = self.eval_model
            print(f"\n[Client] Evaluation mode: {self.eval_model}")
        else:
            self.active_model = self.synthesis_model
            print(f"\n[Client] Synthesis mode: {self.synthesis_model}")

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
                    prompt += f"{m.get('role', '').upper()}: {m.get('content', '')}\n"

                for attempt in range(3):
                    try:
                        response = self.parent.client.models.generate_content(
                            model=self.parent.active_model,
                            contents=prompt,
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
                                                {"content": text},
                                            )
                                        },
                                    )
                                ]

                        return Result(response.text)

                    except Exception as e:
                        if attempt < 2:
                            time.sleep((attempt + 1) * 5)
                        else:
                            raise e


# =====================================================
# Logging
# =====================================================

output_log = []


def log(msg):
    print(msg)
    output_log.append(str(msg))


# =====================================================
# Load Dataset
# =====================================================

df = pd.read_csv("Symptom2Disease.csv")

df["label"] = df["label"].str.lower().str.strip()
df["text"] = df["text"].str.lower().str.strip()


# =====================================================
# Disease Statistics
# =====================================================

log("\n=== Disease Distribution ===")

disease_counts = df["label"].value_counts()

log(disease_counts)
log(f"\nTotal diseases: {df['label'].nunique()}")


# =====================================================
# Auto-select Top 2 Diseases (NO HARDCODING)
# =====================================================

top2 = disease_counts.head(2)

selected_diseases = top2.index.tolist()

log("\n=== Selected Diseases (Top 2) ===")
log(top2)

df_binary = df[df["label"].isin(selected_diseases)].copy()

log("\nBinary Dataset Distribution:")
log(df_binary["label"].value_counts())


# =====================================================
# Train / Validation / Test Split (Stratified)
# =====================================================

train_df, temp_df = train_test_split(
    df_binary,
    test_size=0.30,
    stratify=df_binary["label"],
    random_state=42,
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    stratify=temp_df["label"],
    random_state=42,
)

log("\n=== Dataset Split ===")
log(f"Train: {len(train_df)}")
log(f"Validation: {len(val_df)}")
log(f"Test: {len(test_df)}")


# =====================================================
# Rule Learning Dataset (20 examples per class)
# =====================================================

examples_per_class = 20

rule_learning_df = (
    train_df.groupby("label")
    .sample(n=examples_per_class, random_state=42)
)

log("\n=== Rule Learning Set ===")
log(rule_learning_df["label"].value_counts())


# =====================================================
# Task Definition
# =====================================================

task = Task(
    name="Disease Classification",
    description="Classify disease based on symptoms",
    input_schema={"text": "str"},
    output_schema={"label": "str"},
    type=TaskType.CLASSIFICATION,
    text_field="text",
)

client = GeminiDualClient(api_key="AIzaSyDAFMRudpPaV31IYg3nXO8uU5LVq2r_ujY")

chef = RuleChef(
    task,
    client,
    storage_path="./rulechef_binary",
)


# =====================================================
# Add Examples
# =====================================================

client.set_mode("synthesis")

log("\n=== Adding Examples ===")

for _, row in rule_learning_df.iterrows():
    chef.add_example(
        {"text": row["text"]},
        {"label": row["label"]},
    )


# =====================================================
# Learn Rules
# =====================================================

log("\n=== Learning Rules ===")

start = time.time()

rules = chef.learn_rules()

end = time.time()

log(f"Rule learning time: {end - start:.2f}s")


# =====================================================
# Show Rules
# =====================================================

log("\n=== GENERATED RULES ===")

if rules:
    if isinstance(rules, list):
        log(f"Total rules: {len(rules)}")

        for i, rule in enumerate(rules):
            log(f"\nRule {i + 1}")
            log("-------------------")
            log(str(rule))
    else:
        log(str(rules))
else:
    log("No rules generated")


# =====================================================
# Validation
# =====================================================

client.set_mode("evaluation")

log("\n=== VALIDATION ===")

correct = 0
total = 0

for _, row in val_df.iterrows():
    pred = chef.extract({"text": row["text"]})

    label = pred.get("label") if pred else None

    if label == row["label"]:
        correct += 1

    total += 1

val_acc = correct / total

log(f"Validation Accuracy: {val_acc:.4f}")


# =====================================================
# Test
# =====================================================

log("\n=== TEST ===")

correct = 0
total = 0

for _, row in test_df.iterrows():
    pred = chef.extract({"text": row["text"]})

    label = pred.get("label") if pred else None

    if label == row["label"]:
        correct += 1

    total += 1

test_acc = correct / total

log(f"Test Accuracy: {test_acc:.4f}")


# =====================================================
# Thesis Summary
# =====================================================

log("\n=== THESIS SUMMARY ===")

log(f"Selected Diseases: {selected_diseases}")
log(f"Train Size: {len(train_df)}")
log(f"Val Size: {len(val_df)}")
log(f"Test Size: {len(test_df)}")
log(f"Rule Examples: {len(rule_learning_df)}")
log(f"Validation Accuracy: {val_acc:.4f}")
log(f"Test Accuracy: {test_acc:.4f}")


# =====================================================
# Save Output
# =====================================================

with open("binary_rulechef_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_log))

print("\nSaved: binary_rulechef_results.txt")