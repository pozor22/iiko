FROM python:3.12

RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev

COPY requirements.txt /temp/requirements.txt
COPY backend /backend
WORKDIR /backend
EXPOSE 8000

RUN apt-get update && apt-get install -y postgresql-client build-essential libpq-dev


RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password finance_app-user

USER finance_app-user