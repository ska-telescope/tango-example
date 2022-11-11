ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder:9.3.33"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime:9.3.20"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root

RUN apt-get update && apt-get -y install pkg-config libboost-all-dev tar libffi-dev g++

RUN poetry config virtualenvs.create false

RUN pip install --upgrade pip

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.10/site-packages
