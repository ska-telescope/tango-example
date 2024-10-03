FROM registry.gitlab.com/ska-telescope/ska-base-image/ska-build-python:9b2847bd as build

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY src /app/src

RUN poetry config virtualenvs.create false && poetry install

FROM registry.gitlab.com/ska-telescope/ska-base-image/ska-python:9b2847bd

COPY src /app/src

COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10

ENV PATH=$PATH:/app/src
