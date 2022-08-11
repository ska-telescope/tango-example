ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-bullseye:0.0.0-dev.c5c723b77"

FROM $BASE_IMAGE as requirements-stage

WORKDIR /tmp

RUN pip install --upgrade pip poetry

COPY pyproject.toml poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --dev

FROM $BASE_IMAGE

USER root

RUN apk --update add --no-cache pkgconfig boost-dev tar libffi-dev

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

COPY --chown=tango:tango . /app

RUN  pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt && rm /app/requirements.txt

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages
