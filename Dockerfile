FROM artefact.skatelescope.org/ska-tango-images/pytango-builder:9.3.3.5 as buildenv
FROM artefact.skatelescope.org/ska-tango-images/pytango-runtime:9.3.3.5

RUN sudo apt-get update && sudo apt-get install pkg-config build-essential libboost-python-dev -y

RUN pip install poetry
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
# RUN sudo ln -s /root/.local/bin/poetry /bin/poetry
# RUN poetry config virtualenvs.create false

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./
# FIX: There are pip installed packages on system path which we don't have permissions to remove
# RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
