import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os

BASE_URL = "https://www.indiancancersociety.org"
START_URL = BASE_URL + "/cancer-information/"
headers = {"User-Agent": "Mozilla/5.0"}

# folder to store files
OUTPUT_DIR = "cancer_txt_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------- FETCH PAGE ----------------
def get_soup(url):
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Failed: {url}")
            return None
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# ---------------- SAVE FILE ----------------
def save_to_file(cancer_name, items):
    # make filename safe
    safe_name = re.sub(r"[^\w\s-]", "", cancer_name).strip().replace(" ", "_")
    file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cancer_name + "\n")
        f.write("=" * len(cancer_name) + "\n\n")

        for item in items:
            f.write("- " + item + "\n")

    print(f"Saved: {file_path}")
    

# ---------------- MAIN PAGE EXTRACTION ----------------
def extract_cancer_sections(soup):
    data = {}

    current_cancer = None

    for tag in soup.find_all(["h2", "h3", "p", "li", "a"]):

        # -------- HEADINGS --------
        if tag.name in ["h2", "h3"]:
            text = tag.get_text(" ", strip=True)
            
            #start new section
            if re.match(r"^\d+\s", text):
                current_cancer = text
                data[current_cancer] = {
                    "content": [],
                    "link": None
                }
            # STOP condition (IMPORTANT FIX)
            if current_cancer and not re.match(r"^\d+\s", text):
                # if we hit non-number heading, stop tracking
                current_cancer = None

        # -------- CONTENT --------
        elif tag.name in ["p", "li"]:
            if current_cancer:
                text = tag.get_text(" ", strip=True)
                if text:
                    data[current_cancer]["content"].append(text)

        # -------- KNOW MORE LINK --------
        elif tag.name == "a":
            if (
                current_cancer
                and tag.get_text(strip=True).lower() == "know more"
                and tag.get("href")
            ):
                data[current_cancer]["link"] = urljoin(BASE_URL, tag["href"])

    return data


# ----------------SUBPAGE EXTRACTION ----------------
def extract_symptoms(soup):
    results = []

    for h in soup.find_all(["h2", "h3", "h4"]):
        text = h.get_text(" ", strip=True).lower()

        if "signs" in text or "symptom" in text:

            # grab full section container
            container = h.find_parent()

            for tag in container.find_all(["p", "li"]):
                t = tag.get_text(" ", strip=True)
                if t:
                    results.append(t)

    return results


# ---------------- MAIN FLOW ----------------
main_soup = get_soup(START_URL)
data = extract_cancer_sections(main_soup)

final_output = {}

for cancer, info in data.items():
    print(f"\nProcessing: {cancer}")
    # CASE 1: MAIN PAGE CONTENT EXISTS
    if info["content"]:
        final_output[cancer] = info["content"]

    # CASE 2: FOLLOW LINK
    elif info["link"]:
        #print(f"Fetching subpage: {info['link']}")
        sub_soup = get_soup(info["link"])
        if sub_soup:
            symptoms = extract_symptoms(sub_soup)
            if symptoms:
                final_output[cancer] = symptoms
            else:
                final_output[cancer] = ["No symptoms found"]

    # CASE 3: NOTHING
    else:
        final_output[cancer] = ["No data available"]


# ---------------- FINAL OUTPUT ----------------
print("\n\n=== FINAL OUTPUT ===\n")

for cancer, items in final_output.items():
    print(cancer)
    for item in items:
        print("-", item)


print("\n\n=== SAVING FILES ===\n")

for cancer, items in final_output.items():
    save_to_file(cancer, items)