ARG CAR_OCI_REGISTRY_HOST
FROM ${CAR_OCI_REGISTRY_HOST}/ska-tango-images/pytango-builder:9.3.5 as buildenv
FROM ${CAR_OCI_REGISTRY_HOST}/ska-tango-images/pytango-runtime:9.3.5

USER tango

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install -r /app/requirements.txt

RUN python3 -m pip install . 

