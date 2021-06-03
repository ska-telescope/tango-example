FROM artefact.skatelescope.org/ska-tango-images/pytango-builder:9.3.3.5 as buildenv
FROM artefact.skatelescope.org/ska-tango-images/pytango-runtime:9.3.3.5

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

