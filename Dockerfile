ARG BUILD_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-builder:ca4a9c87"
ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-runtime:ca4a9c87"
FROM $BUILD_IMAGE AS buildenv
FROM $BASE_IMAGE

USER root

RUN apt-get update && apt-get -y install pkg-config libboost-all-dev tar libffi-dev g++ && \
    poetry config virtualenvs.create false && \
    pip install --upgrade pip

WORKDIR /app

COPY --chown=tango:tango pyproject.toml poetry.lock ./

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    sed -i '/pytango/d' poetry-requirements.txt && \
    sed -i '/numpy/d' poetry-requirements.txt && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

COPY --chown=tango:tango src ./

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.10/site-packages
