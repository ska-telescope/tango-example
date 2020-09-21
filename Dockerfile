ARG DOCKER_REGISTRY_USER
ARG DOCKER_REGISTRY_HOST
FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-buildenv:9.3.2.1 as buildenv
FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-runtime:9.3.2.1

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

RUN pip install --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple lmcbaseclasses

CMD ["/venv/bin/python", "/app/module_example/powersupply.py"]
