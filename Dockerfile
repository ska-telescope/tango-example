FROM ska-registry.av.it.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM ska-registry.av.it.pt/ska-docker/ska-python-runtime:latest AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

CMD ["/venv/bin/python", "/app/powersupply/powersupply.py"]
