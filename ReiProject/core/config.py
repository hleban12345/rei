import json
import os

# Папка с данными
DATA_DIR = "rei_data"

# Пути к файлам
CONFIG_FILE = os.path.join(DATA_DIR, "rei_config.json")
MEMORY_FILE = os.path.join(DATA_DIR, "rei_memory.json")
DIALOG_FILE = os.path.join(DATA_DIR, "rei_dialogs.json")
FACTS_FILE = os.path.join(DATA_DIR, "rei_facts.json")
THOUGHTS_FILE = os.path.join(DATA_DIR, "rei_thoughts.json")
DATES_FILE = os.path.join(DATA_DIR, "rei_dates.json")
SYNONYMS_FILE = os.path.join(DATA_DIR, "synonyms.json")

# Универсальная загрузка JSON
def load_json(filename, default=None):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

# Универсальное сохранение JSON
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загрузка конфигурации
def load_config():
    config = load_json(CONFIG_FILE, default={})
    if "name" not in config:
        config["name"] = "Пользователь"
    return config

# Загрузка и разворот синонимов
def load_synonyms():
    raw = load_json(SYNONYMS_FILE, default={})
    synonyms = {}
    for key, values in raw.items():
        for v in values:
            synonyms[v] = key
        synonyms[key] = key
    return synonyms
