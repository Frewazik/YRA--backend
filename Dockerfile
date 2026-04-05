From python:3.12-slim

# Отключаем создания файдов кэша и буферизацию логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаём рабочую папку
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . /app/

# Делаем скрипт запуска исполняемым
RUN chmod +x /app/entrypoint.sh

# Указываем какой скрипт испольнять
ENTRYPOINT ["/app/entrypoint.sh"]
