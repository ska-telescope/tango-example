FROM nexus.engageska-portugal.pt/ska-tango-images/pytango-builder:9.3.3.3-a as buildenv
FROM nexus.engageska-portugal.pt/ska-tango-images/pytango-runtime:9.3.3.3-a

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

RUN pip install ska-tango-base ska-log-transactions --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple

