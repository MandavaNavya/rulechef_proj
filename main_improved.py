


import pandas as pd
import time
from google import genai
from rulechef import RuleChef, Task, TaskType

# ==============================
# Dual-Model Gemini Client
# ==============================
class GeminiDualClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

        # Models
        self.synthesis_model = "gemini-2.5-flash"
        self.eval_model = "gemini-2.5-flash-lite"

        self.active_model = self.synthesis_model
        self.chat = self.Chat(self)

    def set_mode(self, mode="synthesis"):
        if mode == "evaluation":
            self.active_model = self.eval_model
            print(f"\n[Client] Switched to EVALUATION mode ({self.eval_model})")
        else:
            self.active_model = self.synthesis_model
            print(f"\n[Client] Switched to SYNTHESIS mode ({self.synthesis_model})")

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

                max_retries = 3

                for attempt in range(max_retries):
                    try:
                        response = self.parent.client.models.generate_content(
                            model=self.parent.active_model,
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

                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait = (attempt + 1) * 5
                            print(f"Error: {e}. Retrying in {wait}s...")
                            time.sleep(wait)
                        else:
                            raise e


# ==============================
# Initialize Client
# ==============================
client = GeminiDualClient(api_key="AIzaSyDAFMRudpPaV31IYg3nXO8uU5LVq2r_ujY")

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

chef = RuleChef(task, client, storage_path="./rulechef_data2")

# ==============================
# Load Dataset
# ==============================
df = pd.read_csv("Symptom2Disease.csv")
df["label"] = df["label"].str.lower().str.strip()
df["text"] = df["text"].str.lower().str.strip()

# ==============================
# Logging
# ==============================
output_log = []

def log(text):
    print(text)
    output_log.append(str(text))


# ==============================
# STEP 1: Learn Rules
# ==============================
client.set_mode("synthesis")

log("\n--- Adding examples ---")
for _, row in df.iterrows():
    chef.add_example({"text": row["text"]}, {"label": row["label"]})

log("\n--- Learning rules ---")

start_time = time.time()
rules = chef.learn_rules()
end_time = time.time()

synthesis_time = end_time - start_time
log(f"\nSynthesis complete in {synthesis_time:.2f} seconds")


# ==============================
# ✅ SAVE LEARNED RULES
# ==============================
log("\n=== LEARNED RULES ===\n")

if rules:
    if isinstance(rules, list):
        log(f"Total rules generated: {len(rules)}\n")

        for i, rule in enumerate(rules):
            log(f"\n--- Rule {i+1} ---")
            log("-" * 50)
            log(str(rule))
    else:
        log("Single rule object:")
        log(str(rules))
else:
    log("No rules generated")


# ==============================
# STEP 2: Evaluation
# ==============================
client.set_mode("evaluation")

log("\n=== TEST PREDICTIONS ===")

test_inputs = [
    "joint pain and stiffness",
    "My face has rashes and little blisters around my nose",
    "I've been sneezing incessantly and I just can't get this chill to go away",
    "I have a really high fever, and I have problems breathing",
    "My stool has been bloody when I do go, and it hurts",
    "blackheads and pimples that are packed with pus"
]

for text in test_inputs:
    result = chef.extract({"text": text})
    log(f"Input: {text}")
    log(f"Prediction: {result}")
    log("-" * 50)


# ==============================
# FAST EVALUATION
# ==============================
log("\n=== FAST EVALUATION (500 samples) ===")

sample_df = df.sample(n=500, random_state=42)

correct = 0
total = 0

for _, row in sample_df.iterrows():
    pred = chef.extract({"text": row["text"]})

    if pred and pred.get("label") == row["label"]:
        correct += 1

    total += 1

accuracy = correct / total
log(f"Accuracy: {accuracy:.4f} ({correct}/{total})")


# ==============================
# METADATA
# ==============================
metadata = f"""
=== THESIS METADATA ===
Synthesis Model: {client.synthesis_model}
Evaluation Model: {client.eval_model}
Total Samples: {len(df)}
Synthesis Time: {synthesis_time:.2f} seconds
Final Accuracy: {accuracy:.4f}
"""

log(metadata)


# ==============================
# SAVE FILE
# ==============================
with open("improved_results2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_log))

print("\nFinal results saved to final_results.txt")