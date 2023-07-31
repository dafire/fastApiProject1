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
RUN poetry install --only main --no-interaction

# get current git version from github action
ARG GIT_VERSION=develop
ENV GIT_VERSION=${GIT_VERSION}

# copy the content of the local src directory to the working directory
COPY --chown=www-data alembic/ /var/www/alembic
COPY --chown=www-data alembic.ini/ /var/www/alembic.ini
COPY --chown=www-data src/ /var/www/app
COPY --chown=www-data templates/ /var/www/templates

WORKDIR /var/www/app

# command to run on container start
CMD ["poetry", "run", "uvicorn", "--factory", "--loop", "uvloop", "main:create_app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "8000"]
