#
# Never use the network=host mode when running CI jobs, and add extra
# distinguishing identifiers to the network name and container names to
# prevent collisions with jobs from the same project running at the same
# time.
#
ifneq ($(CI_JOB_ID),)
NETWORK_MODE := tangonet-$(CI_JOB_ID)
CONTAINER_NAME_PREFIX := $(PROJECT)-$(CI_JOB_ID)-
else
CONTAINER_NAME_PREFIX := $(PROJECT)-
endif

#
# Defines a default make target so that help is printed if make is called
# without a target
#
.DEFAULT_GOAL := help

pull:  ## download the application image
	docker pull $(IMAGE_TO_TEST)

piplock: build  ## overwrite Pipfile.lock with the image version
	docker run $(IMAGE_TO_TEST) cat /app/Pipfile.lock > $(CURDIR)/Pipfile.lock

interactive:  ## start an interactive session using the project image (caution: R/W mounts source directory to /app)
	docker run --rm -it -p 3000:3000 --name=$(CONTAINER_NAME_PREFIX)dev -e TANGO_HOST=$(TANGO_HOST) \
	  -v $(CURDIR):/app $(IMAGE_TO_TEST) /bin/bash

start_pogo:
	docker run --volume="$(HOME)/tango-example:/home/tango/tango-example" --volume="$(HOME)/.Xauthority:/home/tango/.Xauthority:rw" --env="DISPLAY=$(DISPLAY)" artefact.skatelescope.org/ska-tango-images/tango-pogo:9.6.31.2