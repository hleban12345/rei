import re
import json

INTENTS_FILE = "rei_data/intents.json"
PHRASES_FILE = "rei_data/rei_phrases.json"
SYNONYMS_FILE = "rei_data/synonyms.json"

# Загрузка
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

intents = load_json(INTENTS_FILE)
phrases = load_json(PHRASES_FILE)
synonyms_raw = load_json(SYNONYMS_FILE)

# Разворачивание синонимов
synonyms = {}
for key, values in synonyms_raw.items():
    for v in values:
        synonyms[v] = key
    synonyms[key] = key

def normalize_input(text):
    words = text.lower().strip().split()
    return " ".join(synonyms.get(word, word) for word in words)

def analyze_intent(user_input):
    for intent, keywords in intents.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', user_input):
                return intent
    return None
