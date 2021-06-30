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

start_pogo: ## start the pogo application in a docker container; be sure to have the DISPLAY and XAUTHORITY variable not empty.
	docker run --network host --user $(shell id -u):$(shell id -g) --volume="$(PWD):/home/tango/ska-tango-examples" --volume="$(HOME)/.Xauthority:/home/tango/.Xauthority:rw" --env="DISPLAY=$(DISPLAY)" artefact.skao.int/ska-tango-images-tango-pogo:9.6.32