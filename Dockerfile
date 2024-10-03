FROM registry.gitlab.com/ska-telescope/ska-base-image/ska-build-python:9b2847bd as build

WORKDIR /code

COPY pyproject.toml poetry.lock ./

COPY src /code/src

RUN $HOME/.local/bin/poetry config virtualenvs.create false && $HOME/.local/bin/poetry install

FROM registry.gitlab.com/ska-telescope/ska-base-image/ska-python:9b2847bd

COPY src /code/src

COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10

ENV PATH=$PATH:/code/src
