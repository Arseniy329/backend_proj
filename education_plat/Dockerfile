# 1. Базовий образ Python
FROM python:3.12-slim

# 2. Налаштування, щоб Python не буферизував логи (бачимо їх одразу)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 3. Копіюємо файл із залежностями бекенду
COPY requirements.txt ./

# 4. Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копіюємо код бекенду
COPY . .

EXPOSE 8000

# 6. Команда запуску (наприклад, для Django)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]