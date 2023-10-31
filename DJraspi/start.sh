#!/bin/sh

# Check if secret.txt exists
if [ ! -f "/code/config/config.yml" ]; then
    python config.py
    python manage.py makemigrations --noinput
    python manage.py migrate
    python manage.py createsuperuser --noinput
else
    python manage.py makemigrations --noinput
    python manage.py migrate
fi

# Start server
python manage.py runserver ${LISTEN}:${PORT}
