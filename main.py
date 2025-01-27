import requests
import json
from datetime import datetime, timedelta

url = "https://api.hh.ru/vacancies"

date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

params = {
    "text": "Программист",
    "area": "1",
    "date_from": date_from,
    "per_page": 20,
}

response = requests.get(url, params=params)
response.raise_for_status()
vacancies = response.json()
print(f"Найдено вакансий: {vacancies['found']}")

for item in vacancies['items']:
    published_at = datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%S%z")
    print(f"Название: {item['name']}")
    print(f"Компания: {item['employer']['name']}")
    print(f"Город: {item['area']['name']}")
    print(f"Дата публикации: {published_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Ссылка: {item['alternate_url']}")
    print("-" * 40)