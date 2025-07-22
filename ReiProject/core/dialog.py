import json

DIALOG_FILE = "rei_data/rei_dialogs.json"
dialogs = []
context = []

def load_dialogs():
    global dialogs
    try:
        with open(DIALOG_FILE, "r", encoding="utf-8") as f:
            dialogs = json.load(f)
    except:
        dialogs = []

def save_dialogs():
    with open(DIALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)

def log_dialog(author, message):
    global dialogs, context
    message = message.strip()
    if not message:
        return
    dialogs.append({"author": author, "text": message})
    save_dialogs()
    context.append((author, message))
    if len(context) > 20:
        context.pop(0)

def get_dialog_context():
    return [text for author, text in context[-10:] if author == "Пользователь"]

def get_context():
    return context

def set_context(new_context):
    global context
    context = new_context
