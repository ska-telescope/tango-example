ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango:0.1.0-tc-9.3.3-bullseye-dev.ca7852e3e"
FROM $BASE_IMAGE

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry export --without-hashes --dev -f requirements.txt -o poetry-requirements.txt && pip install -U pip && pip install --no-cache-dir -r poetry-requirements.txt && rm poetry-requirements.txt

USER tango
