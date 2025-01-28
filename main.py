import requests
import json
from datetime import datetime, timedelta


def predict_rub_salary(vacancy):
    salary = vacancy.get('salary')

    if not salary or salary['currency'] != 'RUR':
        return None

    if salary['from'] and salary['to']:
        return (salary['from'] + salary['to']) / 2

    if salary['from']:
        return salary['from'] * 1.2

    if salary['to']:
        return salary['to'] * 0.8

    return None


def get_vacancies_for_language(language):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": f"Программист {language}",
        "area": "1",
        "per_page": 20,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def calculate_salary(languages):
    salary_statistics = {}

    for language in languages:
        vacancies_data = get_vacancies_for_language(language)
        vacancies_found = vacancies_data['found']
        vacancies_processed = 0
        total_salary = 0

        for item in vacancies_data['items']:
            salary = predict_rub_salary(item)
            if salary:
                vacancies_processed += 1
                total_salary += salary

        average_salary = int(total_salary / vacancies_processed) if vacancies_processed > 0 else None
        salary_statistics[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }

    return salary_statistics


def main():
    languages = ['Python', 'Java', "JavaScript", "Go", "PHP"]
    statistics = calculate_salary(languages)
    print(statistics)


if __name__ == '__main__':
    main()


