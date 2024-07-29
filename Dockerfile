ARG BUILD_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-builder:9.5.0"
ARG BASE_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-runtime:9.5.0"

FROM $BUILD_IMAGE AS buildenv

USER root

RUN poetry self update -n 1.8.2
RUN apt-get update && apt-get -y install pkg-config libboost-all-dev tar libffi-dev g++ && \
    poetry config virtualenvs.create false && \
    pip install --upgrade pip

WORKDIR /app

COPY --chown=tango:tango pyproject.toml poetry.lock ./

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

COPY --chown=tango:tango src ./

FROM $BASE_IMAGE

USER root

COPY --from=buildenv /app /app
COPY --from=buildenv /usr/local/lib/python3.10 /usr/local/lib/python3.10  

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.10/site-packages
