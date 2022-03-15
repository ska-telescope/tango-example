ARG BUILD_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-builder:9.3.27-dev.50621b1f"
ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-runtime:9.3.14-dev.50621b1f"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

# Install Poetry
USER root

ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN apt-get update && apt-get install pkg-config build-essential libboost-python-dev  -y

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY --chown=tango:tango . /app

# Install runtime dependencies and the app
RUN poetry install --no-dev

RUN rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create
