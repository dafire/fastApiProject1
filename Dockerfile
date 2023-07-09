FROM node:18 as frontend

WORKDIR /usr/src/app

COPY frontend ./
RUN npm install
RUN npm run build:prod


# set base image (host OS)
FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED 1

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -
ENV PATH="${PATH}:/opt/poetry/bin"

USER www-data

#set the working directory in the container
WORKDIR /var/www

# copy the dependencies file to the working directory
COPY poetry.lock pyproject.toml /var/www/

# install dependencies
RUN poetry install --no-dev --no-interaction

# get current git version from github action
ARG GIT_VERSION=develop
ENV GIT_VERSION=${GIT_VERSION}

# copy the content of the local src directory to the working directory
COPY --chown=www-data app/ /var/www/app

COPY --from=frontend /usr/src/static ./static

WORKDIR /var/www/app

# command to run on container start
CMD ["poetry", "run", "uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips", "*","--host", "0.0.0.0", "--port", "8000"]
