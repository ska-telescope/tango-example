ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder:9.3.17"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime:9.3.15"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

# Install Poetry
USER root

ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN apt-get update && apt-get install pkg-config build-essential libboost-python-dev  -y

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python3 - && \
    rm /usr/local/bin/poetry && \
    chmod a+x /opt/poetry/bin/poetry && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app

COPY --chown=tango:tango . /app

# Install runtime dependencies and the app
RUN poetry install --no-dev

RUN rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create
