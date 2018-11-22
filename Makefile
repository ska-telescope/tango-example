include .make/Makefile.mk

PROJECT = ska-skeleton

# name of the Docker volume used to cache eggs and wheels
CACHE_VOLUME = $(PROJECT)-test-cache

# optional docker run-time arguments
DOCKER_RUN_ARGS =

# defines the image to test
IMAGE_TO_TEST = $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):latest

DOCKER_COMPOSE_COMMAND = PWD=$(CURDIR) \
						 DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) \
						 DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) \
						 docker-compose \
						 -f docker-compose.yml

# defines a function to copy the ./test-harness directory into the container
# and then runs the requested make target in the container. The container is:
#
#   1. attached to the network of the docker-compose test system
#   2. uses a persistent volume to cache Python eggs and wheels so that fewer
#      downloads are required
#   3. uses a transient volume as a working directory, in which untarred files
#      and test output can be written in the container and subsequently copied
#      to the host
#
make = tar -c test-harness/ | \
	   docker run -i --rm --network=$(notdir $(CURDIR))_default \
	   -v $(CACHE_VOLUME):/home/tango/.cache \
	   -v /build -w /build -u tango $(DOCKER_RUN_ARGS) $(IMAGE_TO_TEST) \
	   bash -c "sudo chown tango /build && \
	   tar x --strip-components 1 --warning=all && \
	   make TANGO_HOST=databaseds:10000 $1"

all: test

test: DOCKER_RUN_ARGS = --volumes-from=$(BUILD)
test:
	$(INIT_CACHE)
	$(DOCKER_COMPOSE_COMMAND) up -d
	$(call make,test); \
	  status=$$?; \
	  rm -fr build; \
	  docker cp $(BUILD):/build .; \
	  docker rm -f -v $(BUILD); \
	  $(DOCKER_COMPOSE_COMMAND) down; \
	  exit $$status

devenv:
	$(INIT_CACHE)
	$(DOCKER_COMPOSE_COMMAND) up -d

.PHONY: all test devenv

# Creates Docker volume for use as a cache, if it doesn't exist already
INIT_CACHE = \
	docker volume ls | grep $(CACHE_VOLUME) || \
	docker create --name $(CACHE_VOLUME) -v $(CACHE_VOLUME):/cache $(IMAGE_TO_TEST)

# http://cakoose.com/wiki/gnu_make_thunks
BUILD_GEN = $(shell docker create -v /build $(IMAGE_TO_TEST))
BUILD = $(eval BUILD := $(BUILD_GEN))$(BUILD)