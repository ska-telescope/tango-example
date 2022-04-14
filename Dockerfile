ARG BASE_IMAGE="artefact.skao.int/ska-tango-examples:0.4.19"

FROM $BASE_IMAGE

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages
