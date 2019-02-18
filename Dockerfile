#ARG DOCKER_REGISTRY_USER
#ARG DOCKER_REGISTRY_HOST
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-buildenv:latest AS buildenv
#FROM ${DOCKER_REGISTRY_HOST}/${DOCKER_REGISTRY_USER}/ska-python-runtime:latest AS runtime
FROM ska-registry.av.it.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM ska-registry.av.it.pt/ska-docker/ska-python-runtime:latest AS runtime

#USER root
#RUN runtimeDeps='gdb \
#                 python3-dbg' \
#    && DOCKERHOST=`awk '/^[a-z]+[0-9]+\t00000000/ { printf("%d.%d.%d.%d", "0x" substr($3, 7, 2), "0x" substr($3, 5, 2), "0x" substr($3, 3, 2), "0x" substr($3, 1, 2)) }' < /proc/net/route` \
#    && /usr/local/bin/wait-for-it.sh --host=$DOCKERHOST --port=3142 --timeout=3 --strict --quiet -- echo "Acquire::http::Proxy \"http://$DOCKERHOST:3142\";" > /etc/apt/apt.conf.d/30proxy \
#    && echo "Proxy detected on docker host - using for this build" || echo "No proxy detected on docker host" \
#    && DEBIAN_FRONTEND=noninteractive apt-get update \
#    && apt-get -y install --no-install-recommends $runtimeDeps \
#    && rm -rf /var/lib/apt/lists/* /etc/apt/apt.conf.d/30proxy
#USER tango

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

#USER root
#RUN buildDeps='ca-certificates git' \
#    && DEBIAN_FRONTEND=noninteractive apt-get update \
#    && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends $buildDeps \
#    && su tango -c "/venv/bin/pip install git+https://github.com/ska-telescope/lmc-base-classes.git@story_AT1-163" \
#    && apt-get purge -y --auto-remove $buildDeps \
#    && rm -rf /var/lib/apt/lists/* /home/tango/.cache
#USER tango

#CMD ["gdb","-ex","r","--args","python","/app/powersupply/powersupply.py","test"]

CMD ["/venv/bin/python", "/app/powersupply/powersupply.py"]
