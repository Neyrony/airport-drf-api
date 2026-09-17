FROM python:3.12.10-slim

LABEL maintainer="sserebriy@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 8000

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt && \
    mkdir -p "/files/media/" && \
    adduser --disabled-password --no-create-home django-user --gecos "" && \
    chown -R django-user:django-user "/files/media/" && \
    chmod -R 755 "/files/media/"

COPY . .

USER django-user
