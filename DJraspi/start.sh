#!/bin/sh

# Check if secret.txt exists
if [ ! -f "/code/secret/SECRET_KEY.txt" ]; then
    echo $(openssl rand -base64 32) > /code/secret/SECRET_KEY.txt
fi

export SECRET_KEY=$(cat /code/secret/SECRET_KEY.txt)

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver