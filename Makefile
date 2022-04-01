#
# Project makefile for a Tango project. You should normally only need to modify
# PROJECT below.
#

#
# CAR_OCI_REGISTRY_HOST and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for CAR_OCI_REGISTRY_HOST = artefact.skao.int and overwrites
# PROJECT to give a final Docker tag of
# artefact.skao.int/ska-tango-examples/powersupply
#
PROJECT = ska-tango-examples

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-tango-examples

# RELEASE_NAME is the release that all Kubernetes resources will be labelled
# with
RELEASE_NAME ?= test

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART ?= test-parent
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/

# Fixed variables
# Timeout for gitlab-runner when run locally
TIMEOUT = 86400
# Helm version
HELM_VERSION = v3.3.1
# kubectl version
KUBERNETES_VERSION = v1.19.2

CI_PROJECT_DIR ?= .

KUBE_CONFIG_BASE64 ?=  ## base64 encoded kubectl credentials for KUBECONFIG
KUBECONFIG ?= /etc/deploy/config ## KUBECONFIG location

XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
WEBJIVE ?= false# Enable Webjive
MINIKUBE ?= true ## Minikube or not

CI_PROJECT_PATH_SLUG ?= ska-tango-examples
CI_ENVIRONMENT_SLUG ?= ska-tango-examples

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# Include Python support
include .make/python.mk

# include raw support
include .make/raw.mk

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

# Chart for testing
K8S_CHART = test-parent
K8S_CHARTS = $(K8S_CHART)
HELM_CHARTS = ska-tango-examples/

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS
TANGO_SERVER_PORT ?= 45450## TANGO_SERVER_PORT - fixed listening port for local server
CLUSTER_DOMAIN ?= cluster.local## Domain used for naming Tango Device Servers
K8S_TEST_RUNNER = test-runner-$(CI_JOB_ID)##name of the pod running the k8s-test

# Single image in root of project
OCI_IMAGES = ska-tango-examples

ITANGO_ENABLED ?= false## ITango enabled in ska-tango-base

COUNT ?= 1

PYTHON_VARS_AFTER_PYTEST = -m 'not post_deployment' --forked --disable-pytest-warnings --count=$(COUNT)

ifeq ($(strip $(firstword $(MAKECMDGOALS))),k8s-test)
# need to set the PYTHONPATH since the ska-cicd-makefile default definition 
# of it is not OK for the alpine images
PYTHON_VARS_BEFORE_PYTEST = PYTHONPATH=/app/src:/usr/local/lib/python3.9/site-packages TANGO_HOST=$(TANGO_HOST)
PYTHON_VARS_AFTER_PYTEST := -m 'post_deployment' --disable-pytest-warnings \
	--count=1 --timeout=300 --forked --true-context
endif

HELM_CHARTS_TO_PUBLISH = ska-tango-examples
HELM_CHARTS ?= $(HELM_CHARTS_TO_PUBLISH)

PYTHON_BUILD_TYPE = non_tag_setup

PYTHON_SWITCHES_FOR_FLAKE8=--ignore=F401,W503 --max-line-length=180

ifneq ($(CI_REGISTRY),)
K8S_TEST_TANGO_IMAGE = --set tango_example.tango_example.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set tango_example.tango_example.image.registry=$(CI_REGISTRY)/ska-telescope/ska-tango-examples
K8S_TEST_IMAGE_TO_TEST=$(CI_REGISTRY)/ska-telescope/ska-tango-examples/ska-tango-examples:$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
else
K8S_TEST_TANGO_IMAGE = --set tango_example.tango_example.image.tag=$(VERSION)
K8S_TEST_IMAGE_TO_TEST = artefact.skao.int/ska-tango-examples:$(VERSION)
endif

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
   --set global.exposeDatabaseDS=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.device_server_port=$(TANGO_SERVER_PORT) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set ska-tango-base.itango.enabled=$(ITANGO_ENABLED) \
	--set webjive.enabled=$(WEBJIVE) \
	${K8S_TEST_TANGO_IMAGE} \
	--set event_generator.events_generator.image.tag=$(VERSION)


# override python.mk python-pre-test target
python-pre-test:
	@echo "python-pre-test: running with: $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) pytest $(PYTHON_VARS_AFTER_PYTEST) \
	 --cov=src --cov-report=term-missing --cov-report xml:build/reports/code-coverage.xml --junitxml=build/reports/unit-tests.xml $(PYTHON_TEST_FILE)"

k8s-pre-test: python-pre-test

k8s-pre-template-chart: k8s-pre-install-chart

requirements: ## Install Dependencies
	poetry install

start_pogo: ## start the pogo application in a docker container; be sure to have the DISPLAY and XAUTHORITY variable not empty.
	docker run --network host --user $(shell id -u):$(shell id -g) --volume="$(PWD):/home/tango/ska-tango-examples" --volume="$(HOME)/.Xauthority:/home/tango/.Xauthority:rw" --env="DISPLAY=$(DISPLAY)" $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-pogo:9.6.35

.PHONY: pipeline_unit_test requirements
