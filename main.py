import requests
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2

    if salary_from:
        return salary_from * 1.2

    if salary_to:
        return salary_to * 0.8

    return None


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get("salary")

    if not salary or salary["currency"] != "RUR":
        return None

    return predict_salary(salary.get("from"), salary.get("to"))


def predict_rub_salary_sj(vacancy):
    payment_from = vacancy.get("payment_from")
    payment_to = vacancy.get("payment_to")
    currency = vacancy.get("currency")

    if currency != "rub":
        return None

    return predict_salary(payment_from, payment_to)


def get_vacancies_for_language_from_hh(language, per_page=100):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": f"Программист {language}",
        "area": "1",
        "per_page": per_page,
    }

    all_vacancies = []
    page = 0

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies_data = response.json()

        all_vacancies.extend(vacancies_data["items"])
        if page >= vacancies_data["pages"] - 1 or page > 2:
            break
        page += 1

    return {"found": vacancies_data["found"], "items": all_vacancies}


def get_vacancies_for_language_from_superjob(language, api_key):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
    }

    params = {
        "town": 4,
        "keyword": language,
        "count": 100,
    }

    all_vacancies = []
    page = 0

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_data = response.json()

        all_vacancies.extend(vacancies_data["objects"])

        if not vacancies_data.get("more", False) or page > 2:
            break

        page += 1

    return all_vacancies, vacancies_data["total"]


def calculate_salary_for_hh(languages):
    salary_statistics = {}

    for language in languages:
        vacancies_data_hh = get_vacancies_for_language_from_hh(language)
        vacancies_found_hh = vacancies_data_hh["found"]
        vacancies_processed_hh = 0
        total_salary_hh = 0

        for vacancy in vacancies_data_hh["items"]:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                vacancies_processed_hh += 1
                total_salary_hh += salary

        average_salary_hh = (
            int(total_salary_hh / vacancies_processed_hh)
            if vacancies_processed_hh > 0
            else None
        )

        salary_statistics[language] = {
            "vacancies_found": vacancies_found_hh,
            "vacancies_processed": vacancies_processed_hh,
            "average_salary": average_salary_hh,
        }

    return salary_statistics


def calculate_salary_for_sj(languages, api_key):
    salary_statistics = {}

    for language in languages:
        vacancies_data_sj, vacancies_found_sj = (
            get_vacancies_for_language_from_superjob(language, api_key)
        )
        vacancies_processed_sj = 0
        total_salary_sj = 0

        for vacancy in vacancies_data_sj:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                vacancies_processed_sj += 1
                total_salary_sj += salary

        average_salary_sj = (
            int(total_salary_sj / vacancies_processed_sj)
            if vacancies_processed_sj > 0
            else None
        )

        salary_statistics[language] = {
            "vacancies_found": vacancies_found_sj,
            "vacancies_processed": vacancies_processed_sj,
            "average_salary": average_salary_sj,
        }

    return salary_statistics


def print_table(statistics, platform):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            " Средняя зарплата",
        ]
    ]

    for language, data in statistics.items():
        row = [
            language,
            data["vacancies_found"],
            data["vacancies_processed"],
            data["average_salary"],
        ]
        table_data.append(row)

    table = AsciiTable(table_data)
    print(f"{platform}")
    print(table.table)
    print("\n")


def main():
    load_dotenv()
    api_superjob = os.getenv("SUPERJOB_API_KEY")

    languages = [
        "Python",
        "Java",
        "JavaScript",
        "Go",
        "PHP",
        "C",
        "C#",
        "C++",
        "1c",
    ]

    hh_statistics = calculate_salary_for_hh(languages)
    print_table(hh_statistics, "HeadHunter Moscow")

    sj_statistics = calculate_salary_for_sj(languages, api_superjob)
    print_table(sj_statistics, "SuperJob Moscow")


if __name__ == "__main__":
    main()
