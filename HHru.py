import os
import requests
import sqlite3

BASE_URL = "https://api.hh.ru"

def get_user_input():
    query = os.environ.get("QUERY")
    city = os.environ.get("CITY")
    experience_input = os.environ.get("EXPERIENCE")

    experience_map = {
        "нет опыта": "noExperience",
        "от 1 года": "between1And3",
        "от 3 лет": "between3And6",
        "от 6 лет": "moreThan6"
    }
    experience = experience_map.get(experience_input.lower(), None)

    return {
        'query': query,
        'city': city,
        'experience': experience
    }

def fetch_area_id(city_name):
    response = requests.get(f"{BASE_URL}/areas")
    response.raise_for_status()
    areas = response.json()

    for area in areas:
        for city in area['areas']:
            if city['name'].lower() == city_name.lower():
                return city['id']
    return None

def fetch_vacancies(query, area=None, experience=None):
    params = {
        'text': query,
        'area': area,
        'experience': experience,
        'per_page': 20,
        'page': 0
    }

    response = requests.get(f"{BASE_URL}/vacancies", params=params)
    response.raise_for_status()
    return response.json()

def extract_vacancy_info(vacancies, fields):
    extracted_data = []
    for vacancy in vacancies['items']:
        data = {}
        if 'employer_name' in fields:
            data['employer_name'] = vacancy.get('employer', {}).get('name')
        if 'job_title' in fields:
            data['job_title'] = vacancy.get('name')
        if 'skills' in fields:
            data['skills'] = ', '.join(skill['name'] for skill in vacancy.get('key_skills', [])) or 'Не указаны'
        if 'work_schedule' in fields:
            data['work_schedule'] = vacancy.get('schedule', {}).get('name')
        if 'experience' in fields:
            data['experience'] = vacancy.get('experience', {}).get('name')
        if 'salary' in fields:
            salary = vacancy.get('salary')
            if salary:
                data['salary'] = f"{salary['from']} - {salary['to']} {salary['currency']}" if salary['from'] and salary['to'] else "Не указана"
            else:
                data['salary'] = "Не указана"

        extracted_data.append(data)
    return extracted_data

def save_to_database(vacancies):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    for vacancy in vacancies:
        cursor.execute('''
            INSERT INTO vacancies (employer_name, job_title, skills, work_schedule, experience, salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            vacancy['employer_name'],
            vacancy['job_title'],
            vacancy['skills'],
            vacancy['work_schedule'],
            vacancy['experience'],
            vacancy['salary']
        ))

    conn.commit()
    conn.close()

def analyze_data():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM vacancies')
    total_vacancies = cursor.fetchone()[0]

    cursor.execute('SELECT job_title, COUNT(*) FROM vacancies GROUP BY job_title')
    vacancies_by_title = cursor.fetchall()

    conn.close()

    print(f"Total Vacancies: {total_vacancies}")
    print("Vacancies by Job Title:")
    for title, count in vacancies_by_title:
        print(f"{title}: {count}")
    print('+' * 20)


def main():
    user_input = get_user_input()
    area_id = fetch_area_id(user_input['city'])
    fields = ['employer_name', 'job_title', 'skills', 'work_schedule', 'experience', 'salary']

    vacancies = fetch_vacancies(
        query=user_input['query'],
        area=area_id,
        experience=user_input['experience']
    )
    extracted_data = extract_vacancy_info(vacancies, fields)

    save_to_database(extracted_data)
    analyze_data()

    for job in extracted_data:
        for field, value in job.items():
            print(f"{field.replace('_', ' ').title()}: {value}")
        print("-" * 20)

if __name__ == "__main__":
    main()
