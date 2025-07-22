import json
import datetime
import re
from razdel import tokenize
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

DAYS_RU = {
    "Monday": "понедельник", "Tuesday": "вторник", "Wednesday": "среда",
    "Thursday": "четверг", "Friday": "пятница", "Saturday": "суббота", "Sunday": "воскресенье"
}

MONTHS_RU = {
    "January": "января", "February": "февраля", "March": "марта", "April": "апреля",
    "May": "мая", "June": "июня", "July": "июля", "August": "августа",
    "September": "сентября", "October": "октября", "November": "ноября", "December": "декабря"
}

def load_json_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_today_date_string():
    today = datetime.datetime.now()
    return f"Сегодня {today.day} {MONTHS_RU[today.strftime('%B')]} {today.year} года, {DAYS_RU[today.strftime('%A')]}."

def analyze_meaning(text):
    tokens = [t.text.lower() for t in tokenize(text)]
    lemmas = [(morph.parse(token)[0].normal_form, token) for token in tokens]
    actions = {
        "открыть": "open", "запустить": "open", "включить": "play",
        "проиграть": "play", "показать": "show", "перевести": "translate",
        "найти": "search"
    }
    objects = {
        "стим": "стим", "википедия": "википедия", "гугл": "гугл",
        "ютуб": "ютуб", "видео": "ютуб",
        "погода": "погода", "новости": "новости"
    }
    lemma_sequence = [lemma for lemma, _ in lemmas]
    for i, lemma in enumerate(lemma_sequence):
        if lemma in actions:
            for j in range(i+1, min(i+4, len(lemma_sequence))):
                next_lemma = lemma_sequence[j]
                if next_lemma in objects:
                    return actions[lemma], objects[next_lemma]
    if "погода" in lemma_sequence:
        match = re.search(r"погода в ([а-яА-Яa-zA-Z\- ]+)", text.lower())
        if match:
            return "show_weather_city", match.group(1).strip()
        return "show", "погода"
    return None, None
