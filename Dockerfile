FROM python:3.10-alpine3.17
ENV TZ="Europe/Moscow"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /BrainForces

COPY . .

RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev && \
    pip install --upgrade pip && \
    pip install -r requirements/base.txt