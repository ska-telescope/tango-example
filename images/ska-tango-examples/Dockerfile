ARG BUILD_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-builder-alpine:9.3.31"
ARG BASE_IMAGE="registry.gitlab.com/ska-telescope/ska-tango-images/ska-tango-images-pytango-runtime-alpine:9.3.19"
FROM $BUILD_IMAGE AS buildenv

FROM $BASE_IMAGE

USER root

RUN apk --update add --no-cache pkgconfig boost-dev tar 

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY --chown=tango:tango . /app

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

COPY --chown=tango:tango pyutil.py /usr/local/lib/python3.9/site-packages/tango/pyutil.py

USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages
