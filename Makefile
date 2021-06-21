#
# Project makefile for a Tango project. You should normally only need to modify
# DOCKER_REGISTRY_USER and PROJECT below.
#

#
# DOCKER_REGISTRY_HOST, DOCKER_REGISTRY_USER and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for DOCKER_REGISTRY_HOST = artefact.skao.int and overwrites
# DOCKER_REGISTRY_USER and PROJECT to give a final Docker tag of
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

CI_PROJECT_PATH_SLUG ?= ska-tango-examples
CI_ENVIRONMENT_SLUG ?= ska-tango-examples
$(shell echo 'global:\n  annotations:\n    app.gitlab.com/app: $(CI_PROJECT_PATH_SLUG)\n    app.gitlab.com/env: $(CI_ENVIRONMENT_SLUG)' > gilab_values.yaml)

# define private overrides for above variables in here
-include PrivateRules.mak

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
TEST_RUNNER = test-runner-$(CI_JOB_ID)-$(RELEASE_NAME)

ITANGO_DOCKER_IMAGE = artefact.skao.int/ska-tango-images/tango-itango:9.3.3.7

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#
include .make/release.mk
include .make/docker.mk
include .make/k8s.mk

requirements: ## Install Dependencies
	python3 -m pip install -r requirements.txt
	python3 -m pip install -r requirements-dev.txt

lint: ## Linting src and tests directory
	@mkdir -p build/reports;
	isort --recursive --check-only --profile black src/ tests/
	black --line-length 79 --check src/ tests/
	flake8 --show-source --statistics src/ tests/
	pylint --rcfile=.pylintrc --output-format=parseable src/* tests/* | tee build/code_analysis.stdout
	pylint --output-format=pylint_junit.JUnitReporter src/* tests/* > build/reports/linting-python.xml
	@make --no-print-directory join-lint-reports

# Join different linting reports into linting.xml
# Zero, create linting.xml with empty testsuites
# First, delete newlines from the files for easier parsing
# Second, parse <testsuite> tags in <testsuites> in each file (disregard any attributes in testsuites tag)
# Final, append <testsuite> tags into linting.xml
join-lint-reports: ## Join linting report (chart and python)
	@echo -e "<testsuites>\n</testsuites>" > build/reports/linting.xml; \
	for FILE in build/reports/linting-*.xml; do \
	TEST_RESULTS=$$(tr -d "\n" < $${FILE} | \
	sed -e "s/.*<testsuites[^<]*\(.*\)<\/testsuites>.*/\1/"); \
	TT=$$(echo $${TEST_RESULTS} | sed 's/\//\\\//g'); \
	sed -i.x -e "/<\/testsuites>/ s/.*/$${TT}\n&/" build/reports/linting.xml; \
	rm -f build/reports/linting.xml.x; \
	done
	
apply-formatting: # apply formatting with black
	isort --recursive --profile black src/ tests/
	black --line-length 79 src/ tests/

unit_test: ## Run simulation mode unit tests
	@mkdir -p build; \
	PYTHONPATH=src:src/ska_tango_examples pytest -m "not post_deployment" $(FILE)

pipeline_unit_test: ## Run simulation mode unit tests in a docker container as in the gitlab pipeline
	@docker run --volume="$(HOME)/ska-tango-examples:/home/tango/ska-tango-examples" \
		--env PYTHONPATH=src:src/ska_tango_examples -it $(ITANGO_DOCKER_IMAGE) \
		sh -c "cd /home/tango/ska-tango-examples && make requirements && make unit_test $(FILE)"

.PHONY: all test help k8s lint logs describe namespace delete_namespace kubeconfig kubectl_dependencies k8s_test install-chart uninstall-chart reinstall-chart upgrade-chart interactive
