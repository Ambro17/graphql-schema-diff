FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN pip install graphql-schema-diff

WORKDIR /app

ENTRYPOINT ["schemadiff"]
