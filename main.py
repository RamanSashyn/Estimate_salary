import requests
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable


MOSCOW_AREA_ID = '1'
MOSCOW_TOWN_ID = 4
VACANCIES_PER_PAGE = 100


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


def get_vacancies_for_language_from_hh(language):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": f"Программист {language}",
        "area": MOSCOW_AREA_ID,
        "per_page": VACANCIES_PER_PAGE,
    }

    all_vacancies = []
    page = 0

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies_response = response.json()

        all_vacancies.extend(vacancies_response["items"])
        if page >= vacancies_response["pages"] - 1:
            break
        page += 1

    return vacancies_response["found"], all_vacancies


def get_vacancies_for_language_from_superjob(language, api_key):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
    }

    params = {
        "town": MOSCOW_TOWN_ID,
        "keyword": language,
        "count": VACANCIES_PER_PAGE,
    }

    all_vacancies = []
    page = 0

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_response = response.json()

        all_vacancies.extend(vacancies_response["objects"])

        if not vacancies_response.get("more", False):
            break

        page += 1

    return all_vacancies, vacancies_response["total"]


def fetch_and_analyze_hh_salaries(languages):
    salary_statistics = {}

    for language in languages:
        vacancies_found_hh, vacancies_list_hh = get_vacancies_for_language_from_hh(language)
        vacancies_processed_hh = 0
        total_salary_hh = 0

        for vacancy in vacancies_list_hh:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                vacancies_processed_hh += 1
                total_salary_hh += salary

        average_salary_hh = (
            int(total_salary_hh / vacancies_processed_hh)
            if vacancies_processed_hh
            else None
        )

        salary_statistics[language] = {
            "vacancies_found": vacancies_found_hh,
            "vacancies_processed": vacancies_processed_hh,
            "average_salary": average_salary_hh,
        }

    return salary_statistics


def fetch_and_analyze_sj_salaries(languages, api_key):
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
            if vacancies_processed_sj
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

    for language, statistics_data in statistics.items():
        row = [
            language,
            statistics_data["vacancies_found"],
            statistics_data["vacancies_processed"],
            statistics_data["average_salary"],
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

    hh_statistics = fetch_and_analyze_hh_salaries(languages)
    print_table(hh_statistics, "HeadHunter Moscow")

    sj_statistics = fetch_and_analyze_sj_salaries(languages, api_superjob)
    print_table(sj_statistics, "SuperJob Moscow")


if __name__ == "__main__":
    main()
