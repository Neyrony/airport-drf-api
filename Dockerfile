FROM python:3.12.10-slim

LABEL maintainer="sserebriy@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 8000

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt && \
    adduser --disabled-password --no-create-home django-user --gecos ""

COPY . .

USER django-user
