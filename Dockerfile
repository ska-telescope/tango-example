FROM artefact.skao.int/ska-build-python:0.1.1 as build

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY src /app/src

RUN poetry config virtualenvs.create false && poetry install

FROM artefact.skao.int/ska-tango-images-tango-dsconfig:1.5.13 as tools
FROM artefact.skao.int/ska-build-python:0.1.1

COPY src /app/src

COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=tools /usr/local/bin/retry /usr/local/bin/retry
COPY --from=tools /usr/local/bin/wait-for-it.sh /usr/local/bin/wait-for-it.sh

ENV PATH=$PATH:/app/src
