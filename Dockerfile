
ARG BUILD_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-builder-no-deps-alpine:9.3.32-dev.c04618ca7"
ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-runtime-no-deps-alpine:9.3.21-dev.c04618ca7"

FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root

RUN apk --update add --no-cache pkgconfig boost-dev tar libffi-dev

RUN poetry config virtualenvs.create false

RUN pip install --upgrade pip

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages
