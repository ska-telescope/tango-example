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
PROJECT = tango-example

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= tango-example

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

CI_PROJECT_DIR ?= .

KUBE_CONFIG_BASE64 ?=  ## base64 encoded kubectl credentials for KUBECONFIG
KUBECONFIG ?= /etc/deploy/config ## KUBECONFIG location

XAUTHORITYx ?= ${XAUTHORITY}
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY := $(THIS_HOST):0

CI_PROJECT_PATH_SLUG ?= tango-example
CI_ENVIRONMENT_SLUG ?= tango-example
$(shell echo 'global:\n  annotations:\n    app.gitlab.com/app: $(CI_PROJECT_PATH_SLUG)\n    app.gitlab.com/env: $(CI_ENVIRONMENT_SLUG)' > gilab_values.yaml)

# define private overrides for above variables in here
-include PrivateRules.mak

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
TEST_RUNNER = test-makefile-runner-$(CI_JOB_ID)-$(KUBE_NAMESPACE)-$(RELEASE_NAME)

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

# isort --check-only src/
# isort --check-only tests/
# isort --check-only post-deployment/
lint: ## Linting
	@mkdir -p build/reports; 	
	black --line-length 79 --check src/
	black --line-length 79 --check tests/
	flake8 --show-source --statistics src/
	flake8 --show-source --statistics tests/
	pylint --rcfile=.pylintrc --output-format=parseable src/* tests/* | tee build/code_analysis.stdout
	pylint --output-format=pylint_junit.JUnitReporter src/* tests/* > build/reports/linting-python.xml
	@make --no-print-directory join-lint-reports

# Join different linting reports into linting.xml
# Zero, create linting.xml with empty testsuites
# First, delete newlines from the files for easier parsing
# Second, parse <testsuite> tags in <testsuites> in each file (disregard any attributes in testsuites tag)
# Final, append <testsuite> tags into linting.xml
join-lint-reports:
	@echo -e "<testsuites>\n</testsuites>" > build/reports/linting.xml; \
	for FILE in build/reports/linting-*.xml; do \
	TEST_RESULTS=$$(tr -d "\n" < $${FILE} | \
	sed -e "s/.*<testsuites[^<]*\(.*\)<\/testsuites>.*/\1/"); \
	TT=$$(echo $${TEST_RESULTS} | sed 's/\//\\\//g'); \
	sed -i.x -e "/<\/testsuites>/ s/.*/$${TT}\n&/" build/reports/linting.xml; \
	rm -f build/reports/linting.xml.x; \
	done
	
# isort src/
# isort tests/
# isort post-deployment/
apply-formatting:
	black --line-length 79 src/
	black --line-length 79 tests/

unit_test: ## Run unit tests
	@mkdir -p build; \
	PYTHONPATH=src:src/ska_tango-examples:src/ska_tango-examples pytest 

.PHONY: all test help k8s show lint deploy delete logs describe namespace delete_namespace kubeconfig kubectl_dependencies helm_dependencies rk8s_test k8s_test rlint install-chart uninstall-chart reinstall-chart upgrade-chart
