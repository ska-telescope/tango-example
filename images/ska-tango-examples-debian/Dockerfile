ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder:9.3.28"
ARG BASE_IMAGE="artefact.skao.int/ska-tango-images-pytango-runtime:9.3.16"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

# Install Poetry
USER root

WORKDIR /app

COPY --chown=tango:tango . /app

# Install runtime dependencies and the app
RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

USER tango

RUN poetry config virtualenvs.create false

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create
