import datetime

DAYS_RU = {
    "Monday": "понедельник", "Tuesday": "вторник", "Wednesday": "среда",
    "Thursday": "четверг", "Friday": "пятница", "Saturday": "суббота", "Sunday": "воскресенье"
}

MONTHS_RU = {
    "January": "января", "February": "февраля", "March": "марта", "April": "апреля",
    "May": "мая", "June": "июня", "July": "июля", "August": "августа",
    "September": "сентября", "October": "октября", "November": "ноября", "December": "декабря"
}

def get_local_date_string():
    today = datetime.datetime.now()
    day = today.day
    month = MONTHS_RU[today.strftime("%B")]
    year = today.year
    weekday = DAYS_RU[today.strftime("%A")]
    return f"{day} {month} {year} года, {weekday}"
