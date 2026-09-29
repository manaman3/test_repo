FROM python:3.11-slim

WORKDIR /app

# Устанавливаем корневые сертификаты Минцифры (Russian Trusted CA)
# Без них запросы к platform-api2.max.ru падают с SSL-ошибкой
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && curl -fsSL -o /usr/local/share/ca-certificates/russian_trusted_root_ca_pem.crt \
        https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt \
    && curl -fsSL -o /usr/local/share/ca-certificates/russian_trusted_sub_ca_pem.crt \
        https://gu-st.ru/content/lending/russian_trusted_sub_ca_pem.crt \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Зависимости Python — для кэширования слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY . .

CMD ["python", "main.py"]