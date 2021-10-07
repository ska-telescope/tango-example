ARG CAR_OCI_REGISTRY_HOST
ARG BUILD_IMAGE="${CAR_OCI_REGISTRY_HOST}/ska-tango-images-pytango-builder:9.3.14"
ARG BASE_IMAGE="${CAR_OCI_REGISTRY_HOST}/ska-tango-images-pytango-runtime:9.3.14"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python - && \
    cd /usr/local/bin && \
    chmod a+x /opt/poetry/bin/poetry && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies and the app
RUN poetry install --no-dev

USER tango

RUN poetry config virtualenvs.create false

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create


# RUN python3 -m pip install -r /app/requirements.txt

# RUN python3 -m pip install .

