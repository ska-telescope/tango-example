FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.12 as buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.12

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

RUN python3 -m pip install -r /app/requirements.txt

RUN python3 -m pip install -r requirements.txt

