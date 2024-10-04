# Definizione delle variabili di ambiente
ARG BUILD_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-builder:9.5.0"
ARG BASE_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-runtime:9.5.0"

# Fase di build
FROM $BUILD_IMAGE AS buildenv

USER root

# Installazione di dipendenze
RUN poetry self update -n 1.8.2
RUN apt-get update && apt-get -y install pkg-config libboost-all-dev tar libffi-dev g++ && \
    poetry config virtualenvs.create false && \
    pip install --upgrade pip

WORKDIR /app

COPY --chown=tango:tango pyproject.toml poetry.lock ./

# Esportazione dei requisiti e installazione
RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

# Fase di runtime
FROM $BASE_IMAGE

# Copia dall'immagine buildenv
COPY --from=buildenv /app /app  

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.10/site-packages

# Copia del codice sorgente
COPY --chown=tango:tango src ./
