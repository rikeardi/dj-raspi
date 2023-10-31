#!/bin/sh

# Check if secret.txt exists
if [ ! -f "/code/config/config.yml" ]; then
    python config.py
    export $(grep -v '^#' /code/config/.env | xargs)
    python manage.py makemigrations --noinput
    python manage.py migrate
    python manage.py createsuperuser --noinput --username ${ADMIN_USERNAME} --email ${ADMIN_EMAIL}
else
    export $(grep -v '^#' /code/config/.env | xargs)
    python manage.py makemigrations --noinput
    python manage.py migrate
fi

# Start server
python manage.py runserver ${LISTEN}:${PORT}
