# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput

# Copy project
COPY ./DJraspi/ /code/