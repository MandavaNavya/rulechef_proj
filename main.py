import requests
import json
from openai import OpenAI
from rulechef import RuleChef, Task, TaskType


# 
#  Fetching weather JSON

def fetch_weather(url):
      # Here I'm making a GET request to the weather API
    response = requests.get(url, timeout=10)
     # The API returns JSON, so I directly convert it into a Python dictionary
    return response.json()

# Converting JSON → text

def weather_to_text(data):

    """ Here I'm converting structured JSON into natural language text
     because LLMs and RuleChef work better with text input """
    
    return (
        f"Weather for {data['location']['name']}, {data['location']['country']}. "
        f"Temp: {data['current']['temp_c']}C. "
        f"Condition: {data['current']['condition']['text']}. "
        f"Humidity: {data['current']['humidity']}%. "
        f"Wind: {data['current']['wind_kph']} kph."
    )

#  RuleChef setup (minimal)

def create_rulechef(client):

    """ Here I'm defining a task for RuleChef
    Basically telling it: From input text, extract these fields"""

    task = Task(
        name="Weather Extraction",
        description="Extract weather fields",

        # Input is just text
        input_schema={"text": "str"},
        # Output should contain these structured fields
        output_schema={
            "location": "str",
            "temperature": "float",
            "condition": "str",
            "humidity": "int",
            "wind_speed": "float"
        },
        # This is a transformation task (text → structured data)
        type=TaskType.TRANSFORMATION,
    )
    """Now I create the RuleChef engine """
    return RuleChef(
        task,
        client=client,
        # I don't want it to auto-trigger, I'll control it manually
        auto_trigger=False,
        # controling fallback manually for much safer
        llm_fallback=False, 
         # Not using Grex optimization
        use_grex=False,
        model="llama-3.1-8b-instant"
    )



# Weather Pipeline using LLM

class WeatherPipeline:
    def __init__(self):
        # Here I'm initializing the LLM client (Groq endpoint)
        self.client = OpenAI(
            api_key="YOUR_API_KEY",
            base_url="https://api.groq.com/openai/v1"
        )
         # Initialize RuleChef with this LLM client
        self.chef = create_rulechef(self.client)

  
    def llm_extract(self, text):

        """STRICT JSON extraction using LLM"""
        # Here I directly call the LLM to extract structured data

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            # Force model to return JSON only
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract weather data.\n"
                        "Return ONLY JSON with:\n"
                        "location, temperature, condition, humidity, wind_speed"
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        # Convert response string → dictionary
        return json.loads(response.choices[0].message.content)

  
    def clean_rulechef_output(self, result):

        """Take best value from noisy RuleChef output"""

        cleaned = {}

        for key, values in result.items():
            if not values:
                continue

            # pick best candidate (longest meaningful string)
            best = max(values, key=lambda x: len(str(x)))

            # Sometimes RuleChef returns nested dicts
            if isinstance(best, dict):
                cleaned[key] = (
                    best.get("location")
                    or best.get("value")
                    or best.get("condition")
                )
            else:
                cleaned[key] = best

        return cleaned

    # extraction logic
    def extract(self, text):

        # RuleChef

        result = self.chef.extract({"text": text})

        if result:
            cleaned = self.clean_rulechef_output(result)

            # If still garbage → fallback
            # If extraction looks good enough → return it
            if cleaned and len(cleaned) >= 3:
                return cleaned
        #If RuleChef fails → fallback to LLM
        print("Fallback to LLM...")
        return self.llm_extract(text)

   # Full pipeline execution
    def run(self, url):

        """Get raw weather JSON
        Convert JSON → text and Extract structured info"""

        data = fetch_weather(url)
        text = weather_to_text(data)

        print("INPUT TEXT:")
        print(text)

        result = self.extract(text)

        print("\nFINAL RESULT:")
        print(result)

        return result



# Run

if __name__ == "__main__":

    """ Weather API details"""

    BASE_URL = "http://api.weatherapi.com/v1/current.json?"
    API_KEY = "YOUR_API_KEY"
    CITY = "Vienna"

     # Construct full API URL
    url = f"{BASE_URL}key={API_KEY}&q={CITY}"

    # Run pipeline
    pipeline = WeatherPipeline()
    pipeline.run(url)