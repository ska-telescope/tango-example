ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder-alpine:9.3.28"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime-alpine:9.3.16"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root

RUN apk --update add --no-cache pkgconfig boost-dev tar 

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages
