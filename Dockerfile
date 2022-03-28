ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder-alpine:9.3.15"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime-alpine:9.3.15"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root

RUN apk --update add --no-cache pkgconfig boost-dev tar 

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python3 - && \
    rm /usr/local/bin/poetry && \
    chmod a+x /opt/poetry/bin/poetry && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry install --no-dev

USER tango

