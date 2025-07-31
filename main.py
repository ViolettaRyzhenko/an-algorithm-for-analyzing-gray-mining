import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import time
import subprocess
import matplotlib.dates as mdates
from datetime import datetime

# Запускаем newvar.py как отдельный процесс
subprocess.Popen(["python", "makedata.py"])

# Конфигурация подключения к базе данных PostgreSQL
DB_CONFIG = {
    "dbname": "Electricity_otchet_1",
    "user": "postgres",
    "password": "111",
    "host": "localhost",
    "port": "5432"
}

# Функция для получения данных о потреблении энергии
def get_energy_data():
    """Получает все данные о потреблении энергии из базы данных"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, consumption FROM energy_consumption ORDER BY timestamp ASC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Функция для анализа аномалий с использованием Z-score
def detect_anomalies(data):
    """Анализирует скачки потребления (аномалии)"""
    if len(data) < 2:
        return []

    timestamps, values = zip(*data)
    values = np.array(values)

    mean_val = np.mean(values)
    std_dev = np.std(values)

    anomalies = []
    for i, val in enumerate(values):
        z_score = (val - mean_val) / std_dev if std_dev != 0 else 0
        if z_score > 3 or val > 5000:  # Скачки или высокое потребление
            anomalies.append((timestamps[i], val, round(z_score, 2)))

    return anomalies

# Функция для визуализации данных
def plot_energy_data(data, anomalies):
    """Строит график потребления энергии с выделением аномалий"""
    timestamps, values = zip(*data)

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, label="Потребление энергии (Вт)", color="blue", marker='o')

    # Отмечаем аномалии
    if anomalies:
        anomaly_times, anomaly_values, _ = zip(*anomalies)
        plt.scatter(anomaly_times, anomaly_values, color="red", label="Аномалии", zorder=3)

        # Подписываем аномальные точки
        for i, txt in enumerate(anomaly_values):
            plt.annotate(f"{txt:.2f} Вт", (anomaly_times[i], anomaly_values[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.xlabel("Дата и время")
    plt.ylabel("Потребление энергии (Вт)")
    plt.title("Анализ потребления энергии")
    plt.legend()
    
    # Форматирование оси X
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y\n%H:%M'))  # ДД.ММ.ГГ и ЧЧ:ММ
    plt.xticks(rotation=45)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Главная функция анализа и визуализации
def analyze_and_plot():
    data = get_energy_data()
    if not data:
        print("Нет данных для анализа.")
        return
    
    anomalies = detect_anomalies(data)

    if anomalies:
        print("Обнаружены аномалии, возможно скрытый майнинг:")
        for anomaly in anomalies:
            timestamp, energy, z_score = anomaly
            print(f"Время: {timestamp}, Потребление: {energy} Вт, Z-скор: {z_score}")
    else:
        print("Скрытый майнинг не найден. Потребление в пределах нормы.")

    plot_energy_data(data, anomalies)

# Запуск анализа в реальном времени
if __name__ == "__main__":
    while True:
        analyze_and_plot()
        time.sleep(30)  # Проверяем каждые 30 секунд