# Use an official Python runtime as a parent image
FROM arm64v8/python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/

RUN 'pip install -r requirements.txt'

# Copy project
COPY ./DJraspi/ /code/

# Run start.sh
CMD ["start.sh"]
