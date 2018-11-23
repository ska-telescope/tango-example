FROM registry.gitlab.com/ska-telescope/ska-docker/ska-python:latest

CMD /venv/bin/python /app/powersupply/powersupply.py test
