import os
import webbrowser
import subprocess
import platform
import psutil
import datetime
import tkinter as tk
import threading
import time
from tkinter import ttk

def open_known_website(command):
    sites = {
        "ютуб": "https://www.youtube.com",
        "википедия": "https://ru.wikipedia.org",
        "гугл": "https://www.google.com",
        "яндекс": "https://ya.ru",
        "новости": "https://news.google.com",
        "погода": "https://weather.com",
        "переводчик": "https://translate.google.com",
    }
    for key, url in sites.items():
        if key in command:
            webbrowser.open(url)
            return f"Открываю {key.title()}."
    return "Я не знаю такой сайт. Попробуй сказать 'поиск [название]'."

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return "Вот результаты поиска."

def open_folder(path):
    try:
        os.startfile(path)
        return "Открываю папку."
    except Exception as e:
        return f"Не удалось открыть: {e}"

def open_program(path):
    try:
        subprocess.Popen(path)
        return "Открываю программу."
    except Exception as e:
        return f"Не удалось запустить: {e}"

def shutdown():
    os.system("shutdown /s /t 0")

def restart():
    os.system("shutdown /r /t 0")

def sleep():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def launch_advanced_monitor():
    def update_data():
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            cpu_label.config(text=f"CPU: {cpu}%")
            ram_label.config(text=f"RAM: {ram}%")

            cpu_bar['value'] = cpu
            ram_bar['value'] = ram

            time.sleep(1)

    window = tk.Toplevel()
    window.title("Rei - Системный монитор")
    window.geometry("400x200")

    ttk.Label(window, text="Мониторинг системы Rei", font=("Segoe UI", 14)).pack(pady=10)

    cpu_label = ttk.Label(window, text="CPU: ...")
    cpu_label.pack()
    cpu_bar = ttk.Progressbar(window, length=300)
    cpu_bar.pack()

    ram_label = ttk.Label(window, text="RAM: ...")
    ram_label.pack()
    ram_bar = ttk.Progressbar(window, length=300)
    ram_bar.pack()

    threading.Thread(target=update_data, daemon=True).start()
    
show_system_monitor = launch_advanced_monitor