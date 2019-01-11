#ARG DOCKER_REGISTRY_USER
#ARG DOCKER_REGISTRY_HOST
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-buildenv:latest AS buildenv
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-runtime:latest AS runtime
FROM registry.gitlab.com/ska-telescope/ska-docker/ska-python-buildenv:latest AS buildenv
FROM registry.gitlab.com/ska-telescope/ska-docker/ska-python-runtime:latest AS runtime

CMD ["/venv/bin/python", "/app/powersupply/powersupply.py"]
