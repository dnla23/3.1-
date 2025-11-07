"""
Генератор тестовых данных для варианта 25: службы такси
Создаёт:
- data/taxi_companies.csv
- data/trips.xlsx
- data/expenses.json
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

def generate_taxi_companies():
    companies = [
        {"company_code": "TX001", "company_name": "Такси Быстро"},
        {"company_code": "TX002", "company_name": "Городской Такси"},
        {"company_code": "TX003", "company_name": "Эконом Такси"},
        {"company_code": "TX004", "company_name": "Бизнес Такси"},
        {"company_code": "TX005", "company_name": "Ночной Маршрут"},
    ]
    df = pd.DataFrame(companies)
    df['country'] = 'Россия'
    df['founded_year'] = [2008, 2012, 2015, 2010, 2018]
    df.to_csv('data/taxi_companies.csv', index=False, encoding='utf-8')
    print("✓ data/taxi_companies.csv создан")
    return df

def generate_trips(companies_df, months=6):
    # генерируем агрегат по месяцам
    rows = []
    today = datetime.now().date()
    for _, row in companies_df.iterrows():
        for m in range(months):
            period = (today - pd.DateOffset(months=m)).replace(day=1).date()
            trips_count = random.randint(500, 8000)
            avg_price = round(random.uniform(2.0, 15.0) * 100, 2)  # в рублях: 200..1500
            rows.append({
                "taxi_company_code": row['company_code'],
                "period_date": period.strftime("%Y-%m-%d"),
                "trips_count": trips_count,
                "avg_trip_price": avg_price
            })
    df = pd.DataFrame(rows)
    df.to_excel('data/trips.xlsx', index=False)
    print("✓ data/trips.xlsx создан")
    return df

def generate_expenses(companies_df, months=6):
    rows = []
    today = datetime.now().date()
    for _, row in companies_df.iterrows():
        for m in range(months):
            period = (today - pd.DateOffset(months=m)).replace(day=1).date()
            fuel = round(random.uniform(100000, 800000), 2)   # руб
            maintenance = round(random.uniform(20000, 200000), 2)
            rows.append({
                "taxi_company_code": row['company_code'],
                "period_date": period.strftime("%Y-%m-%d"),
                "fuel_cost": fuel,
                "maintenance_cost": maintenance
            })
    with open('data/expenses.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("✓ data/expenses.json создан")
    return rows

def consolidate_and_save():
    # Простая консолидация в csv (используется в папке data/)
    df_comp = pd.read_csv('data/taxi_companies.csv', dtype=str)
    df_trips = pd.read_excel('data/trips.xlsx', dtype=str)
    df_exp = pd.read_json('data/expenses.json', dtype=str)

    # Приведём типы
    df_trips['trips_count'] = df_trips['trips_count'].astype(int)
    df_trips['avg_trip_price'] = df_trips['avg_trip_price'].astype(float)
    df_exp['fuel_cost'] = df_exp['fuel_cost'].astype(float)
    df_exp['maintenance_cost'] = df_exp['maintenance_cost'].astype(float)

    # Объединяем по company_code и period_date
    df = pd.merge(df_trips, df_exp, how='outer', on=['taxi_company_code', 'period_date'])
    df = pd.merge(df, df_comp[['company_code', 'company_name']], how='left', left_on='taxi_company_code', right_on='company_code')
    # Рассчёт revenue/expenses/net_profit
    df['revenue'] = df['trips_count'].fillna(0) * df['avg_trip_price'].fillna(0)
    df['expenses'] = df['fuel_cost'].fillna(0) + df['maintenance_cost'].fillna(0)
    df['net_profit'] = df['revenue'] - df['expenses']

    df.to_csv('data/consolidated_taxi_data.csv', index=False, encoding='utf-8')
    # summary per company (all periods)
    summary = df.groupby(['taxi_company_code','company_name'], as_index=False).agg({
        'revenue':'sum',
        'expenses':'sum',
        'net_profit':'sum',
        'trips_count':'sum'
    })
    summary = summary.rename(columns={'taxi_company_code':'company_code', 'trips_count':'total_trips'})
    summary.to_csv('data/taxi_profit_summary.csv', index=False, encoding='utf-8')
    print("✓ data/consolidated_taxi_data.csv и data/taxi_profit_summary.csv созданы")

def main():
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✓ Создана папка data/")
    df_comp = generate_taxi_companies()
    generate_trips(df_comp, months=6)
    generate_expenses(df_comp, months=6)
    consolidate_and_save()

if __name__ == "__main__":
    main()
