#!/bin/bash

echo "Применяем миграции БД"
python manage.py migrate --noinput

echo "Запускаем сервер"
exec python manage.py runserver 0.0.0.0:8000
