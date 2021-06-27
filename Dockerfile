FROM artefact.skatelescope.org/ska-tango-images/pytango-builder:9.3.3.5 as buildenv
FROM artefact.skatelescope.org/ska-tango-images/pytango-runtime:9.3.3.5

USER root

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-dev --no-root
