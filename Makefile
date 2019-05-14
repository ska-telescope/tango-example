#
# Project makefile for a Tango project. You should normally only need to modify
# DOCKER_REGISTRY_USER and PROJECT below.
#

#
# DOCKER_REGISTRY_HOST, DOCKER_REGISTRY_USER and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for DOCKER_REGISTRY_HOST (=rnexus.engageska-portugal.pt) and overwrites
# DOCKER_REGISTRY_USER and PROJECT to give a final Docker tag of
# nexus.engageska-portugal.pt/tango-example/powersupply
#
DOCKER_REGISTRY_USER:=tango-example
PROJECT = powersupply


# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= default

# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test

# HELM_CHART the chart name
HELM_CHART ?= tango-example

# INGRESS_HOST is the host name used in the Ingress resource definition for
# publishing services via the Ingress Controller
INGRESS_HOST ?= $(HELM_RELEASE).$(HELM_CHART).local


# Fixed variables
# Timeout for gitlab-runner when run locally
TIMEOUT = 86400
# Helm version
HELM_VERSION = v2.13.1
# kubectl version
KUBERNETES_VERSION = v1.14.1

# Docker, K8s and Gitlab CI variables
# gitlab-runner debug mode - turn on with non-empty value
RDEBUG ?=
# gitlab-runner executor - shell or docker
EXECUTOR ?= shell
# DOCKER_HOST connector to gitlab-runner - local domain socket for shell exec
DOCKER_HOST ?= unix:///var/run/docker.sock
# DOCKER_VOLUMES pass in local domain socket for DOCKER_HOST
DOCKER_VOLUMES ?= /var/run/docker.sock:/var/run/docker.sock
# registry credentials - user/pass/registry - set these in PrivateRules.mak
DOCKER_REGISTRY_USER_LOGIN ?=  ## registry credentials - user - set in PrivateRules.mak
CI_REGISTRY_PASS_LOGIN ?=  ## registry credentials - pass - set in PrivateRules.mak
CI_REGISTRY ?= gitlab.com/ska-telescope/tango-example
KUBE_CONFIG_BASE64 ?=  ## base64 encoded kubectl credentials for KUBECONFIG
KUBECONFIG ?= /etc/deploy/config ## KUBECONFIG location

# define private overrides for above variables in here
-include PrivateRules.mak

# Test runner - run to completion job in K8s
TEST_RUNNER = test-runner-$(HELM_CHART)-$(HELM_RELEASE)

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#
include .make/Makefile.mk

#
# IMAGE_TO_TEST defines the tag of the Docker image to test
#
IMAGE_TO_TEST = $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):latest

#
# CACHE_VOLUME is the name of the Docker volume used to cache eggs and wheels
# used during the test procedure. The volume is not used during the build
# procedure
#
CACHE_VOLUME = $(PROJECT)-test-cache

# optional docker run-time arguments
DOCKER_RUN_ARGS =

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

ifeq ($(OS),Windows_NT)
    $(error Sorry, Windows is not supported yet)
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		DISPLAY ?= :0.0
		NETWORK_MODE ?= host
		XAUTHORITY_MOUNT := /tmp/.X11-unix:/tmp/.X11-unix
		XAUTHORITY ?= /hosthome/.Xauthority
		# /bin/sh (=dash) does not evaluate 'docker network' conditionals correctly
		SHELL := /bin/bash
	endif
	ifeq ($(UNAME_S),Darwin)
		IF_INTERFACE := $(shell netstat -nr | awk '{ if ($$1 ~/default/) { print $$6} }')
		DISPLAY := $(shell ifconfig $(IF_INTERFACE) | awk '{ if ($$1 ~/inet$$/) { print $$2} }'):0
		# network_mode = host doesn't work on MacOS, so fix to the internal network
		NETWORK_MODE := tangonet
		XAUTHORITY_MOUNT := $(HOME):/hosthome:ro
		XAUTHORITY := /hosthome/.Xauthority
	endif
endif

#
# When running in network=host mode, point devices at a port on the host
# machine rather than at the container.
#
ifeq ($(NETWORK_MODE),host)
TANGO_HOST := $(shell hostname):10000
MYSQL_HOST := $(shell hostname):3306
else
# distinguish the bridge network from others by adding the project name
NETWORK_MODE := $(NETWORK_MODE)-$(PROJECT)
TANGO_HOST := $(CONTAINER_NAME_PREFIX)databaseds:10000
MYSQL_HOST := $(CONTAINER_NAME_PREFIX)tangodb:3306
endif


DOCKER_COMPOSE_ARGS := DISPLAY=$(DISPLAY) XAUTHORITY=$(XAUTHORITY) TANGO_HOST=$(TANGO_HOST) \
		NETWORK_MODE=$(NETWORK_MODE) XAUTHORITY_MOUNT=$(XAUTHORITY_MOUNT) MYSQL_HOST=$(MYSQL_HOST) \
		DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) \
		CONTAINER_NAME_PREFIX=$(CONTAINER_NAME_PREFIX) COMPOSE_IGNORE_ORPHANS=true

#
# Defines a default make target so that help is printed if make is called
# without a target
#
.DEFAULT_GOAL := help

#
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
	   docker run -i --rm --network=$(NETWORK_MODE) \
	   -e TANGO_HOST=$(TANGO_HOST) \
	   -v $(CACHE_VOLUME):/home/tango/.cache \
	   -v /build -w /build -u tango $(DOCKER_RUN_ARGS) $(IMAGE_TO_TEST) \
	   bash -c "sudo chown -R tango:tango /build && \
	   tar x --strip-components 1 --warning=all && \
	   make TANGO_HOST=$(TANGO_HOST) $1"

test: DOCKER_RUN_ARGS = --volumes-from=$(BUILD)
test: build up ## test the application
	$(INIT_CACHE)
	$(call make,test); \
	  status=$$?; \
	  rm -fr build; \
	  docker cp $(BUILD):/build .; \
	  docker rm -f -v $(BUILD); \
	  $(MAKE) down; \
	  exit $$status

pull:  ## download the application image
	docker pull $(IMAGE_TO_TEST)

up: build  ## start develop/test environment
ifneq ($(NETWORK_MODE),host)
	docker network inspect $(NETWORK_MODE) &> /dev/null || ([ $$? -ne 0 ] && docker network create $(NETWORK_MODE))
endif
	$(DOCKER_COMPOSE_ARGS) docker-compose up -d

piplock: build  ## overwrite Pipfile.lock with the image version
	docker run $(IMAGE_TO_TEST) cat /app/Pipfile.lock > $(CURDIR)/Pipfile.lock

interactive: up
interactive:  ## start an interactive session using the project image (caution: R/W mounts source directory to /app)
	docker run --rm -it -p 3000:3000 --name=$(CONTAINER_NAME_PREFIX)dev -e TANGO_HOST=$(TANGO_HOST) --network=$(NETWORK_MODE) \
	  -v $(CURDIR):/app $(IMAGE_TO_TEST) /bin/bash

down:  ## stop develop/test environment and any interactive session
	docker ps | grep $(CONTAINER_NAME_PREFIX)dev && docker stop $(PROJECT)-dev || true
	$(DOCKER_COMPOSE_ARGS) docker-compose down
ifneq ($(NETWORK_MODE),host)
	docker network inspect $(NETWORK_MODE) &> /dev/null && ([ $$? -eq 0 ] && docker network rm $(NETWORK_MODE)) || true
endif

#
# defines a function to copy the ./test-harness directory into the K8s TEST_RUNNER
# and then runs the requested make target in the container.
# 
k8s_test = tar -c test-harness/ | \
		kubectl run $(TEST_RUNNER) \
		--namespace $(KUBE_NAMESPACE) -i --wait --restart=Never \
		--image-pull-policy=IfNotPresent \
		--image=$(IMAGE_TO_TEST) -- \
		/bin/bash -c "tar xv --strip-components 1 --warning=all && \
		make TANGO_HOST=databaseds-$(HELM_CHART)-$(HELM_RELEASE):10000 $1"

# tar -cv test-harness/ | kubectl run test-runner -n default -i --wait --restart=Never --image-pull-policy=IfNotPresent --image=nexus.engageska-portugal.pt/tango-example/powersupply:latest -- /bin/bash -c "tar xv --strip-components 1 --warning=all && make TANGO_HOST=databaseds-tango-example-test:10000 test"

k8s_test: ## test the application on K8s
	$(call k8s_test,test); \
	  status=$$?; \
	  kubectl --namespace $(KUBE_NAMESPACE) logs $(TEST_RUNNER); \
		kubectl --namespace $(KUBE_NAMESPACE) delete pod $(TEST_RUNNER); \
	  exit $$status

rlint:  ## run lint check on Helm Chart using gitlab-runner
	if [ -n "$(RDEBUG)" ]; then DEBUG_LEVEL=debug; else DEBUG_LEVEL=warn; fi && \
	gitlab-runner --log-level $${DEBUG_LEVEL} exec $(EXECUTOR) \
	--docker-privileged \
	--docker-disable-cache=false \
	--docker-host $(DOCKER_HOST) \
	--docker-volumes  $(DOCKER_VOLUMES) \
	--docker-pull-policy always \
	--timeout $(TIMEOUT) \
	--env "DOCKER_HOST=$(DOCKER_HOST)" \
  --env "DOCKER_REGISTRY_USER_LOGIN=$(DOCKER_REGISTRY_USER_LOGIN)" \
  --env "CI_REGISTRY_PASS_LOGIN=$(CI_REGISTRY_PASS_LOGIN)" \
  --env "CI_REGISTRY=$(CI_REGISTRY)" \
	lint-check-chart || true

# K8s testing with local gitlab-runner
# Run the powersupply tests in the TEST_RUNNER run to completion Pod:
#   set namespace
#   install dependencies for Helm and kubectl
#   deploy into namespace
#   run test in run to completion Pod
#   extract Pod logs
#   set test return code
#   delete
#   delete namespace
#   return result
rk8s_test:  ## run k8s_test on K8s using gitlab-runner
	if [ -n "$(RDEBUG)" ]; then DEBUG_LEVEL=debug; else DEBUG_LEVEL=warn; fi && \
	KUBE_NAMESPACE=`git rev-parse --abbrev-ref HEAD | tr -dc 'A-Za-z0-9\-' | tr '[:upper:]' '[:lower:]'` && \
	gitlab-runner --log-level $${DEBUG_LEVEL} exec $(EXECUTOR) \
	--docker-privileged \
	--docker-disable-cache=false \
	--docker-host $(DOCKER_HOST) \
	--docker-volumes  $(DOCKER_VOLUMES) \
	--docker-pull-policy always \
	--timeout $(TIMEOUT) \
	--env "DOCKER_HOST=$(DOCKER_HOST)" \
	--env "DOCKER_REGISTRY_USER_LOGIN=$(DOCKER_REGISTRY_USER_LOGIN)" \
	--env "CI_REGISTRY_PASS_LOGIN=$(CI_REGISTRY_PASS_LOGIN)" \
	--env "CI_REGISTRY=$(CI_REGISTRY)" \
	--env "KUBE_CONFIG_BASE64=$(KUBE_CONFIG_BASE64)" \
	--env "KUBECONFIG=$(KUBECONFIG)" \
	--env "KUBE_NAMESPACE=$${KUBE_NAMESPACE}" \
	test-chart || true

# Utility target to install Helm dependencies
helm_dependencies:
	which helm ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
	curl "https://kubernetes-helm.storage.googleapis.com/helm-$(HELM_VERSION)-linux-amd64.tar.gz" | tar zx; \
	mv linux-amd64/helm /usr/bin/; \
	fi
	helm version --client

# Utility target to install K8s dependencies
kubectl_dependencies:
	@([ -n "$(KUBE_CONFIG_BASE64)" ] && [ -n "$(KUBECONFIG)" ]) || (echo "unset variables [KUBE_CONFIG_BASE64/KUBECONFIG] - abort!"; exit 1)
	@which kubectl ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
		curl -L -o /usr/bin/kubectl "https://storage.googleapis.com/kubernetes-release/release/$(KUBERNETES_VERSION)/bin/linux/amd64/kubectl"; \
		chmod +x /usr/bin/kubectl; \
		mkdir -p /etc/deploy; \
		echo $(KUBE_CONFIG_BASE64) | base64 -d > $(KUBECONFIG); \
	fi
	@echo -e "\nkubectl client version:"
	@kubectl version --client
	@echo -e "\nkubectl config view:"
	@kubectl config view
	@echo -e "\nkubectl config get-contexts:"
	@kubectl config get-contexts
	@echo -e "\nkubectl version:"
	@kubectl version

kubeconfig: ## export current KUBECONFIG as base64 ready for KUBE_CONFIG_BASE64
	@KUBE_CONFIG_BASE64=`kubectl config view --flatten | base64 -w 0`; \
	echo "KUBE_CONFIG_BASE64: $$(echo $${KUBE_CONFIG_BASE64} | cut -c 1-40)..."; \
	echo "appended to: PrivateRules.mak"; \
	echo -e "\n\n# base64 encoded from: kubectl config view --flatten\nKUBE_CONFIG_BASE64 = $${KUBE_CONFIG_BASE64}" >> PrivateRules.mak

ingress_check:  ## curl test Tango REST API - https://tango-controls.readthedocs.io/en/latest/development/advanced/rest-api.html#tango-rest-api-implementations
	@echo "---------------------------------------------------"
	@echo "Test HTTP:"; echo ""
	curl -u "tango-cs:tango" -XGET http://$(INGRESS_HOST)/tango/rest/rc4/hosts/databaseds-tango-example-$(HELM_RELEASE)/10000 | json_pp
	@echo "", echo ""
	@echo "---------------------------------------------------"
	@echo "Test HTTPS:"; echo ""
	curl -k -u "tango-cs:tango" -XGET https://$(INGRESS_HOST)/tango/rest/rc4/hosts/databaseds-tango-example-$(HELM_RELEASE)/10000 | json_pp
	@echo ""

help:  ## show this help.
	@echo "make targets:"
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""; echo "make vars (+defaults):"
	@grep -hE '^[0-9a-zA-Z_-]+ \?=.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = " \?\= "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\#\#/  \#/'


.PHONY: all test up down help k8s show lint deploy delete logs describe mkcerts localip namespace delete_namespace ingress_check kubeconfig kubectl_dependencies helm_dependencies rk8s_test k8s_test rlint

# Creates Docker volume for use as a cache, if it doesn't exist already
INIT_CACHE = \
	docker volume ls | grep $(CACHE_VOLUME) || \
	docker create --name $(CACHE_VOLUME) -v $(CACHE_VOLUME):/cache $(IMAGE_TO_TEST)

# http://cakoose.com/wiki/gnu_make_thunks
BUILD_GEN = $(shell docker create -v /build $(IMAGE_TO_TEST))
BUILD = $(eval BUILD := $(BUILD_GEN))$(BUILD)
