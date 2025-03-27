FROM artefact.skao.int/ska-tango-images-tango-dsconfig:1.5.13 as tools
FROM artefact.skao.int/ska-build-python:0.1.3 as build

WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1

#no-root is required because in the build
#step we only want to install dependencies
#not the code under development
RUN poetry install --no-root

FROM artefact.skao.int/ska-python:0.1.4

#Adding the virtualenv binaries
#to the PATH so there is no need
#to activate the venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=tools /usr/local/bin/retry /usr/local/bin/retry
COPY --from=tools /usr/local/bin/wait-for-it.sh /usr/local/bin/wait-for-it.sh
COPY src /app/src

#Add source code to the PYTHONPATH
#so python is able to find our package
#Add packages from the venv to the PYTHONPATH
ENV PYTHONPATH="/app/src:app/.venv/lib/python3.10/site-packages/:${PYTHONPATH}"