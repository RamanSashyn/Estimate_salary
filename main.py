import requests
import json
from datetime import datetime, timedelta

url = "https://api.hh.ru/vacancies"

popular_languages = [
    "Python",
    "JavaScript",
    "Java",
    "C#",
    "PHP",
    "C",
    "C++",
    "CSS",
    "Go",
]

language_vacancies = {}

for language in popular_languages:
    params = {
        "text": f"Программист {language}",
        "area": "1",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancies = response.json()
    language_vacancies[language] = vacancies['found']

print(language_vacancies)

