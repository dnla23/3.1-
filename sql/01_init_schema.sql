-- Создание базы данных для анализа авиакомпаний
-- Задание 30: Авиакомпании, Рейсы, Билеты - расчет общей выручки для каждой авиакомпании

-- Таблица авиакомпаний
CREATE TABLE IF NOT EXISTS airlines (
    airline_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    founded_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица рейсов
CREATE TABLE IF NOT EXISTS flights (
    flight_id SERIAL PRIMARY KEY,
    airline_id INTEGER REFERENCES airlines(airline_id),
    flight_number VARCHAR(20) NOT NULL,
    departure_city VARCHAR(100),
    arrival_city VARCHAR(100),
    departure_date DATE,
    passengers_count INTEGER CHECK (passengers_count >= 0),
    aircraft_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица билетов
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    flight_id INTEGER REFERENCES flights(flight_id),
    avg_ticket_price DECIMAL(10, 2) CHECK (avg_ticket_price >= 0),
    ticket_class VARCHAR(20) DEFAULT 'Economy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_flights_airline_id ON flights(airline_id);
CREATE INDEX IF NOT EXISTS idx_tickets_flight_id ON tickets(flight_id);
CREATE INDEX IF NOT EXISTS idx_flights_departure_date ON flights(departure_date);

-- Представление для расчета выручки авиакомпаний
CREATE OR REPLACE VIEW airline_revenue AS
SELECT 
    a.airline_id,
    a.name AS airline_name,
    a.country,
    COUNT(DISTINCT f.flight_id) AS total_flights,
    SUM(f.passengers_count) AS total_passengers,
    AVG(t.avg_ticket_price) AS avg_ticket_price,
    SUM(f.passengers_count * t.avg_ticket_price) AS total_revenue
FROM airlines a
LEFT JOIN flights f ON a.airline_id = f.airline_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id
GROUP BY a.airline_id, a.name, a.country
ORDER BY total_revenue DESC NULLS LAST;
