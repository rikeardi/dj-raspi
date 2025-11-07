# Use an official Python runtime as a parent image
FROM arm64v8/python:3.12-alpine

RUN apk add --no-cache bash 
RUN apk add --no-cache pigpio --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt

VOLUME ["/code/config"]
VOLUME ["/code/data"]

# Copy project
COPY DJraspi /code

# Run start.sh
CMD ["start.sh"]
