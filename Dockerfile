FROM python:3.10-alpine3.16
ENV TZ="Europe/Moscow"

COPY requirements/base.txt /temp/requirements.txt
COPY brainforces /brainforces
WORKDIR /brainforces
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password brainforces-user

USER brainforces-user
