FROM artefact.skao.int/ska-build:0.1.0 as build

WORKDIR /code

COPY pyproject.toml poetry.lock ./

COPY src /code/src

RUN $HOME/.local/bin/poetry config virtualenvs.create false && $HOME/.local/bin/poetry install

FROM registry.gitlab.com/ska-telescope/ska-base-image/ska-python:0.1.0-dev.cc9db6838

COPY src /code/src

COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10

ENV PATH=$PATH:/code/src
