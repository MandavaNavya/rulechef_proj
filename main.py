import os
import re
from google import genai
from rulechef import RuleChef, Task, TaskType

# Gemini OpenAI-Compatible Client
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


# Initialize client
client = GeminiOpenAIClient(
    api_key="AIzaSyCikuwYXWjbN1U3J5wJSAOHkvfKvFd_yVg",
    model="gemini-2.5-flash"
)

# Task
task = Task(
    name="Cancer Type Classification",
    description="Classify cancer type based on symptoms",
    input_schema={"text": "str"},
    output_schema={"label": "str"},
    type=TaskType.CLASSIFICATION,
    text_field="text",
)

chef = RuleChef(task, client, storage_path="./rulechef_data2")
DATA_DIR = "cancer_txt_files"

# Label extraction
def extract_label(filename):
    label = filename.replace(".txt", "").lower()
    # label = label.replace("_symptoms", "")
    label = label.replace("cancer_of_the_", "")
    label = label.replace("cancer_in_the_", "")
    label = label.replace("cancer", "")
    label = label.strip("_")

    corrections = {
        "paancreas": "pancreas",
        "prostrate": "prostate"
    }

    return corrections.get(label, label)

# Load dataset
def load_dataset(data_dir):
    examples = []

    print("\n--- STEP 1: Checking DATA_DIR ---")
    #print("DATA_DIR:", data_dir)

    files = os.listdir(data_dir)
    #print("Files found:", files)

    for file in files:
        file_path = os.path.join(data_dir, file)

        if not file.endswith(".txt"):
            continue

        label = extract_label(file)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = re.split(r'[.\n]', text)

        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) < 25:
                continue
            examples.append((chunk, label))

    print("\nTotal examples:", len(examples))
    return examples

# Load dataset
dataset = load_dataset(DATA_DIR)

# Collect output
output_log = []

def log(text):
    print(text)
    output_log.append(str(text))

# Add examples
log("\n--- Adding examples ---")

for i, (text, label) in enumerate(dataset):
    chef.add_example({"text": text}, {"label": label})

# Learn rules
log("\n--- Learning rules ---")
rules = chef.learn_rules()

log("\n=== FINAL RULES ===\n")

if rules:
    log(rules)
else:
    log("No rules generated")

test_inputs = [
    "I have a lump in my breast and pain",
    "there is bleeding after intercourse",
    "irregular periods and pelvic pain",
    "breast swelling and discharge",
    "persistent cough and weight loss",
    "difficulty swallowing and throat pain"
]

log("\n=== TEST PREDICTIONS ===\n")

for text in test_inputs:
    result = chef.extract({"text": text})

    log(f"Input: {text}")
    log(f"Prediction: {result}")
    log("-" * 50)

# Evaluation
eval_result = chef.evaluate()
log(f"\nEvaluation: {eval_result}")

# Per-rule evaluation
metrics = chef.get_rule_metrics()
log(f"\nPer-rule evaluation: {metrics}")

# Save to file
output_file = "results.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_log))

print(f"\n Results saved to {output_file}")