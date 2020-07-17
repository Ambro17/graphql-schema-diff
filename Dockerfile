FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

LABEL author="Ambro17"

RUN pip install graphql-schema-diff

WORKDIR /app

# Reference: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#entrypoint
# All arguments after <image> will be handled by schemadiff. 
# If no args are specified it will run schemadiff --help
ENTRYPOINT ["schemadiff"]
CMD ["--help"]
