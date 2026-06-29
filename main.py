import pandas as pd
import time
from google import genai
from rulechef import RuleChef, Task, TaskType

# ==============================
# Gemini Client
# ==============================
class GeminiOpenAIClient:
    def __init__(self, api_key, model="gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.chat = self.Chat(self)

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
                    role = m.get("role", "").upper()
                    content = m.get("content", "")
                    prompt += f"{role}: {content}\n"

                response = self.parent.client.models.generate_content(
                    model=self.parent.model,
                    contents=prompt
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


# ==============================
# Initialize Client
# ==============================
client = GeminiOpenAIClient(
    api_key="AIzaSyDAFMRudpPaV31IYg3nXO8uU5LVq2r_ujY",
    model="gemini-2.5-flash-lite"   
)

# ==============================
# Define Task
# ==============================
task = Task(
    name="Disease Classification",
    description="Classify disease based on symptom description",
    input_schema={"text": "str"},
    output_schema={"label": "str"},
    type=TaskType.CLASSIFICATION,
    text_field="text",
)

chef = RuleChef(task, client, storage_path="./rulechef_data")

# ==============================
# Load Dataset
# ==============================
df = pd.read_csv("Symptom2Disease.csv")

# Clean data
df["label"] = df["label"].str.lower().str.strip()
df["text"] = df["text"].str.lower().str.strip()

print("Total samples:", len(df))
print("Unique labels:", df["label"].nunique())

# OPTIONAL: speed up training
# df = df.sample(n=300, random_state=42)

# ==============================
# Logging Setup
# ==============================
output_log = []

def log(text):
    print(text)
    output_log.append(str(text))

# ==============================
# Add Examples
# ==============================
log("\n--- Adding examples ---")

for _, row in df.iterrows():
    chef.add_example(
        {"text": row["text"]},
        {"label": row["label"]}
    )

# ==============================
# Learn Rules + Time Tracking
# ==============================
log("\n--- Learning rules ---")

start_time = time.time()
rules = chef.learn_rules()
end_time = time.time()

elapsed_time = end_time - start_time
log(f"\n Time taken to learn rules: {elapsed_time:.2f} seconds")

# ==============================
# Print Rules
# ==============================
log("\n=== FINAL RULES ===\n")

if rules:
    if isinstance(rules, list):
        for i, rule in enumerate(rules):
            log(f"Rule {i+1}: {rule}")
    else:
        log(str(rules))
else:
    log("No rules generated")

# ==============================
# Test Predictions
# ==============================
test_inputs = [
    "joint pain and stiffness",
    "My face has rashes and little blisters around my nose",
    "I've been sneezing incessantly and I just can't get this chill to go away",
    "I have a really high fever, and I have problems breathing",
    "My stool has been bloody when I do go, and it hurts",
    "blackheads and pimples that are packed with pus"
]

log("\n=== TEST PREDICTIONS ===\n")

for text in test_inputs:
    result = chef.extract({"text": text})
    log(f"Input: {text}")
    log(f"Prediction: {result}")
    log("-" * 50)

# ==============================
# FAST EVALUATION (NO LLM LOOP)
# ==============================
log("\n=== FAST EVALUATION (1000 samples) ===")

sample_df = df.sample(n=500, random_state=42)

correct = 0
total = 0

for _, row in sample_df.iterrows():
    pred = chef.extract({"text": row["text"]})

    predicted_label = pred.get("label") if pred else None
    true_label = row["label"]

    if predicted_label == true_label:
        correct += 1

    total += 1

accuracy = correct / total

log(f"Accuracy: {accuracy:.2f}")
log(f"Correct: {correct} / {total}")

# ==============================
# Rule Metrics (optional)
# ==============================
try:
    metrics = chef.get_rule_metrics()
    log(f"\nPer-rule evaluation: {metrics}")
except Exception as e:
    log(f"\nRule metrics error: {e}")

# ==============================
# Metadata
# ==============================
log("\n=== METADATA ===")
log(f"Total samples: {len(df)}")
log(f"Total labels: {df['label'].nunique()}")
log(f"Training time (seconds): {elapsed_time:.2f}")

# ==============================
# Save Results
# ==============================
with open("main_results4.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_log))

print("\nResults saved to results.txt")