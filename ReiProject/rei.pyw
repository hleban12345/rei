import json
import wikipedia
import os
import random
import datetime
import webbrowser
import requests
import pymorphy2
import ctypes
import re
import traceback
from core.date_utils import get_local_date_string
from core import dialog as dialog_module
from core.utils import load_json_file, analyze_meaning, get_today_date_string
from core import date_utils
from core import actions as action_module
from core import context as context_module
from core import intent as intent_module
from core import memory as memory_module
from core.actions import launch_advanced_monitor
from core.voice import speak
from rei_games import rps_game
from razdel import tokenize
import subprocess
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import simpledialog, scrolledtext

wikipedia.set_lang("ru")

# --- API
OPENWEATHER_API_KEY = "5b84c8871fcb05119f3d3f855429a2fb"


# --- Файлы
CONFIG_FILE = "rei_data/rei_config.json"
MEMORY_FILE = "rei_data/rei_memory.json"
DIALOG_FILE = "rei_data/rei_dialogs.json"
FACTS_FILE = "rei_data/rei_facts.json"
THOUGHTS_FILE = "rei_data/rei_thoughts.json"

# --- Загрузка
config = {}
memory = memory_module.load_memory()
dialog_module.load_dialogs()

fun_facts = load_json_file(FACTS_FILE)
rei_thoughts = load_json_file(THOUGHTS_FILE)

if not isinstance(fun_facts, list): fun_facts = ["Факты не загружены."]
if not isinstance(rei_thoughts, list): rei_thoughts = ["Мысли не загружены."]

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config["name"] = "Пользователь"

context_rules = context_module.load_context_rules()

# --- Вспомогательные функции

def load_special_dates():
    try:
        with open("rei_data/rei_dates.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("special_dates", [])
    except: return []

def check_today_special_date():
    today = datetime.datetime.now()
    return [d["message"] for d in load_special_dates() if d["month"] == today.month and d["day"] == today.day]

# --- Ответ
def respond_to(text):
    user_input = intent_module.normalize_input(text.strip())
    context_text = dialog_module.get_dialog_context()
    dialog_module.log_dialog("Пользователь", user_input)

    matched = context_module.check_context_response(dialog_module.get_context(), context_rules)
    if matched:
        reply = random.choice(matched) if isinstance(matched, list) else matched
        return reply

    # --- Интенты из JSON
    intent = intent_module.analyze_intent(user_input)
    if intent and intent in intent_module.phrases:
        if intent == "exit":
            root.after(300, root.destroy)
        return random.choice(intent_module.phrases[intent])

    # --- Стандартные команды
    if user_input in ["факт"]:
        return "Факт: " + random.choice(fun_facts)
    if user_input in ["мысль"]:
        return "Мысль: " + random.choice(rei_thoughts)
    if user_input in ["помощь"]:
        return """Вот что я умею:
- факт / мысль
- открой [название]
- вики [тема]
- погода [город]
- переведи [фраза]
- новости
- память / очисти память
- история
- игра камень/ножницы/бумага
"""

    if user_input == "память":
        return "Вот что я запомнила:\n" + "\n".join(f"• {k} → {v[0]}" for k, v in memory.items()) if memory else "Память пуста."
    if user_input == "очисти память":
        memory.clear()
        memory_module.save_memory(memory)
        return "Память очищена."

    if user_input.startswith("вики "):
        return "По Википедии:\n" + action_module.wiki_search(user_input[5:].strip())
    if user_input.startswith("переведи "):
        return "Перевод: " + action_module.translate_text(user_input[9:].strip())
    if user_input.startswith("погода "):
        return "Погода: " + action_module.get_weather(user_input[7:].strip())
    if user_input.startswith("найди "):
        return action_module.open_website(user_input[6:].strip())

    if "город" not in config:
        config["город"] = "Усть-Каменогорск"
    
    if "монитор" in command or "система" in command:
        launch_advanced_monitor()
        return "Открываю мониторинг системы."
    
    if user_input.startswith("воспроизведи ") or user_input.startswith("ютуб "):
        return action_module.play_music(user_input.replace("воспроизведи ", "").replace("ютуб ", "").strip())
    if user_input == "новости":
        return "Вот последние новости:\n" + action_module.get_news()
    if user_input.startswith("игра "):
        move = user_input[5:].strip()
        if move in ["камень", "ножницы", "бумага"]:
            return rps_game.play_rps(move)
        else:
            return "Напиши: игра камень, игра ножницы или игра бумага."
    
    if "какое сегодня число" in user_input or "сегодняшняя дата" in user_input:
       add_reply("Сегодня " + get_local_date_string())
       return
    
    if user_input == "история":
        last = dialogs[-10:] if len(dialogs) >= 1 else []
        history = "\n".join(f"{d['автор']}: {d['сообщение']}" for d in last)
        add_reply("Вот последние сообщения:\n" + history)
	
    if user_input.startswith("игра "):
        move = user_input[5:].strip()
        if move in ["камень", "ножницы", "бумага"]:
            result = rps_game.play_rps(move)
            add_reply(result)
        else:
            add_reply("Напиши: игра камень, игра ножницы или игра бумага.")
        return
    
    if "шашки" in user_input or "игра в шашки" in user_input:
        subprocess.Popen(["pythonw", "rei_games/checkers_game.pyw"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Запускаю шашки. Я буду играть за чёрных."


    if user_input.startswith("поиск "):
        query = user_input.replace("поиск ", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Ищу в Google: {query}"

    if user_input.startswith("открой ") or user_input.startswith("запусти "):
        return action_module.open_program(user_input)

    if user_input.startswith("воспроизведи ") or user_input.startswith("ютуб "):
        query = user_input.replace("воспроизведи ", "").replace("ютуб ", "").strip()
        return action_module.play_music(query)
 
    # --- Анализ действия
    action, obj = analyze_meaning(user_input)
    if action == "show_weather_city":
        return "Погода: " + action_module.get_weather(obj)
    if action == "show" and obj == "погода":
        return "Погода: " + action_module.get_weather(config.get("город", "Усть-Каменогорск"))
    if action == "show" and obj == "новости":
        return "Вот последние новости:\n" + action_module.get_news()
    if action == "translate":
        return "Перевод: " + action_module.translate_text(user_input.replace("переведи", "").strip())
    if action == "open":
        return action_module.open_website(obj)
    if action == "play" and obj == "ютуб":
        return action_module.play_music(user_input)

    # --- Команда "какое сегодня число"
    if any(phrase in user_input for phrase in ["какое сегодня число", "сегодняшняя дата", "сейчас какое число"]):
        add_reply("Сегодня " + date_utils.get_local_date_string())

    # --- Завершение работы
    if any(phrase in user_input for phrase in ["заверши работу", "пока", "до встречи", "до свидания", "завершение работы"]):
        root.after(800, root.destroy)
        return "Хорошо. До встречи!"

    # --- Запоминание
    if user_input in memory:
        return memory[user_input][0]

    reply = simpledialog.askstring("Обучение", f"Я не знаю как ответить на «{user_input}». Научи меня:")
    if reply:
        memory[user_input] = [reply]
        memory_module.save_memory(memory)
        dialog_module.log_dialog("Rei", reply)
        return "Запомнила"

    return "Окей, может в другой раз."

# --- GUI
def add_reply(message):
    if not message: return
    recent_replies = [msg for author, msg in dialog_module.get_context()[-5:] if author == "Rei"]
    if message.strip().lower() in recent_replies: return
    dialog_module.log_dialog("Rei", message)
    chatbox.insert(tk.END, "Rei: " + message + "\n")
    chatbox.yview(tk.END)
    speak(text)
    
def send_message():
    text = entry.get("1.0", tk.END).strip()
    if text:
        entry.delete("1.0", tk.END)
        chatbox.insert(tk.END, f"Вы: {text}\n")
        chatbox.yview(tk.END)
        reply = respond_to(text)
        add_reply(reply)

root = tk.Tk()
root.title("Rei - Виртуальный помощник")
root.geometry("600x800")
root.configure(bg="#2b4c6f")
try: root.iconbitmap("rei_icon.ico")
except: pass

frame_chat = tk.Frame(root)
frame_chat.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
chatbox = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, font=("Segoe UI", 11, "bold"),
                                    bg="#dce6f2", fg="#000", insertbackground="#000")
chatbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
style_scrollbar = tk.Scrollbar(frame_chat, command=chatbox.yview, bg="#608bb0")
style_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chatbox.config(yscrollcommand=style_scrollbar.set)

entry = tk.Text(root, height=1, font=("Segoe UI", 12,), 
                bg="#f0f8ff", fg="#000", insertbackground="#000")
entry.pack(padx=10, pady=(0, 5), fill=tk.X)
entry.bind("<Shift-Return>", lambda e: entry.insert(tk.INSERT, "\n"))
entry.bind("<Return>", lambda e: (send_message(), "break"))
tk.Button(root, text="Отправить", command=send_message,
          bg="#608bb0", fg="#fff", font=("Segoe UI", 12)).pack(pady=(0, 5))

def styled_button(text, row, col, cmd):
    tk.Button(frame, text=text, command=cmd, width=10, font=("Segoe UI", 10, "bold"),
              bg="#4e6f8f", fg="#fff").grid(row=row, column=col, padx=5, pady=5)

frame = tk.Frame(root, bg="#2b4c6f")
frame.pack()
styled_button("Вики", 0, 0, lambda: add_reply(respond_to("вики " + (simpledialog.askstring("Википедия", "О чём ты хочешь узнать?") or ""))))
styled_button("Погода", 0, 1, lambda: add_reply(respond_to("погода " + (simpledialog.askstring("Погода", "Город:") or ""))))
styled_button("Новости", 0, 2, lambda: add_reply(respond_to("новости")))
styled_button("Помощь", 1, 0, lambda: add_reply(respond_to("помощь")))
styled_button("Память", 1, 1, lambda: add_reply(respond_to("память")))
styled_button("Очистка", 1, 2, lambda: add_reply(respond_to("очисти память") if (simpledialog.askstring("Очистка", "Напиши 'да' для очистки:") == "да") else add_reply("Отмена очистки.")))
styled_button("Система", 2, 1, action_module.show_system_monitor)

def show_system_monitor():
    win = tk.Toplevel(root)
    win.title("Монитор системы")
    import tkinter as tk
    main_window = tk._default_root
    main_window.update_idletasks()
    x = main_window.winfo_x()
    y = main_window.winfo_y()
    width = main_window.winfo_width()

    win.geometry(f"400x300+{x + width + 10}+{y}")

    win.configure(bg="#1e2d3a")
    labels = {}

    def update_info():
        data = action_module.get_system_status()
        if "error" in data:
            labels["error"].config(text="Ошибка: " + data["error"])
        else:
            labels["os"].config(text=f"ОС: {data['os']}")
            labels["device"].config(text=f"Имя: {data['device']}")
            labels["boot"].config(text=f"Загрузка: {data['boot']}")
            labels["cpu"].config(text=f"ЦП: {data['cpu']}")
            labels["ram"].config(text=f"Память: {data['ram']}")
            labels["disk"].config(text=f"Диск: {data['disk']}")
            labels["ip"].config(text=f"IP: {data['ip']}")
        win.after(1000, update_info)

    for key in ["os", "device", "boot", "cpu", "ram", "disk", "ip", "error"]:
        lbl = tk.Label(win, text="", font=("Consolas", 10), fg="#d6f0ff", bg="#1e2d3a", anchor="w")
        lbl.pack(fill=tk.X, padx=10, pady=2)
        labels[key] = lbl

    update_info()

def set_russian_keyboard():
    try:
        ctypes.windll.user32.LoadKeyboardLayoutW("00000419", 1)
        ctypes.windll.user32.ActivateKeyboardLayout(0x0419, 0)
    except: pass
set_russian_keyboard()

try:
   for msg in check_today_special_date():
       add_reply(msg)

   if not check_today_special_date():
       hour = datetime.datetime.now().hour
       greeting = "Доброе утро" if hour < 12 else "Добрый вечер" if hour >= 18 else "Добрый день"
       add_reply(f"{greeting}, {config.get('name', 'Пользователь')}! Чем могу быть полезна?")
except Exception as e:
    print("Ошибка при запуске Rei:")
    traceback.print_exc()
    
entry.focus()
root.mainloop()
