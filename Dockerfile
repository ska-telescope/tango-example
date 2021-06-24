FROM artefact.skao.int/ska-tango-images/pytango-builder:9.3.4 as buildenv
FROM artefact.skao.int/ska-tango-images/pytango-runtime:9.3.4

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install -r /app/requirements.txt

RUN python3 -m pip install . 

