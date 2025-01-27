import requests
import json
from datetime import datetime, timedelta


def predict_rub_salary(vacancy):
    salary = vacancy['salary']

    if not salary or salary['currency'] != 'RUR':
        return None

    if salary['from'] and salary['to']:
        return (salary['from'] + salary['to']) / 2

    if salary['from']:
        return salary['from'] * 1.2

    if salary['to']:
        return salary['to'] * 0.8

    return None


def main():
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": "Программист Python",
        "area": "1",
        "per_page": 20,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancies = response.json()

    for item in vacancies["items"]:
        expected_salary = predict_rub_salary(item)
        print(expected_salary)


if __name__ == '__main__':
    main()


