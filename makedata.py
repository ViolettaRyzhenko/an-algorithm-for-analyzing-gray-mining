import time
import psycopg2
from datetime import datetime
import random

# Конфигурация базы данных
DB_CONFIG = {
    "dbname": "Electricity_otchet_1",
    "user": "postgres",
    "password": "111",
    "host": "localhost",
    "port": "5432"
}

def insert_random_data():
    """Функция для автоматического добавления данных в PostgreSQL"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        energy_consumption = random.uniform(4000, 6000)  # случайные данные
        energy_consumption = round(energy_consumption, 2)  # Округляем до 2 знаков после запятой

        cur.execute(
            "INSERT INTO energy_consumption (timestamp, consumption) VALUES (%s, %s)",
            (timestamp, energy_consumption)
        )
        conn.commit()
        print(f"Добавлены данные: {timestamp} - {energy_consumption:.2f} Вт")

        time.sleep(30)  # Ждём 30 секунд

    cur.close()
    conn.close()

if __name__ == "__main__":
    insert_random_data()