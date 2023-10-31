#!/bin/sh

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver