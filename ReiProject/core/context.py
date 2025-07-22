import json
import os

CONTEXT_FILE = "rei_data/rei_contexts.json"

def load_context_rules():
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def check_context_response(dialog_history, rules):
    """
    Проверяет, подходит ли текущий диалог под какое-либо контекстное правило.
    :param dialog_history: список кортежей (автор, текст) из последних реплик
    :param rules: список правил из rei_contexts.json
    :return: строка-ответ, если найдено правило, иначе None
    """
    if len(dialog_history) < 2:
        return None

    # Последние две реплики: одна от Rei, одна от Пользователя
    last_rei = ""
    last_user = ""
    for author, text in reversed(dialog_history):
        if author == "Rei" and not last_rei:
            last_rei = text.strip().lower()
        elif author == "Пользователь" and not last_user:
            last_user = text.strip().lower()
        if last_user and last_rei:
            break

    current_input = dialog_history[-1][1].strip().lower() if dialog_history[-1][0] == "Пользователь" else ""

    for rule in rules:
        prev = [s.lower().strip() for s in rule.get("прошлый", [])]
        curr = [s.lower().strip() for s in rule.get("текущий", [])]

        if (last_user in prev or last_rei in prev) and current_input in curr:
            return rule.get("ответ")

    return None
