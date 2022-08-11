ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-bullseye:0.0.0-dev.c5c723b77"
FROM $BASE_IMAGE

WORKDIR /app

RUN poetry export --without-hashes --dev -f requirements.txt -o poetry-requirements.txt && pip install -U pip && pip install -no-cache-dir -r poetry-requirements.txt && rm poetry-requirements.txt

COPY --chown=tango:tango . /app

USER tango
