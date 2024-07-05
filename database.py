import sqlite3


def create_database():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_name TEXT,
            job_title TEXT,
            skills TEXT,
            work_schedule TEXT,
            experience TEXT,
            salary TEXT
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
