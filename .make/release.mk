#
#   Copyright 2015  Xebia Nederland B.V.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
ifeq ($(strip $(PROJECT)),)
  NAME=$(shell basename $(CURDIR))
else
  NAME=$(PROJECT)
endif

RELEASE_SUPPORT := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))/.make-release-support

ifeq ($(strip $(DOCKER_REGISTRY_HOST)),)
  DOCKER_REGISTRY_HOST = nexus.engageska-portugal.pt
endif

ifeq ($(strip $(DOCKER_REGISTRY_USER)),)
  DOCKER_REGISTRY_USER = ska-docker
endif

IMAGE=$(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(NAME)

VERSION=$(shell . $(RELEASE_SUPPORT) ; getVersion)
TAG=$(shell . $(RELEASE_SUPPORT); getTag)

SHELL=/bin/bash

DOCKER_BUILD_CONTEXT=.
DOCKER_FILE_PATH=Dockerfile

.PHONY: pre-build docker-build post-build build release patch-release minor-release major-release tag check-status check-release showver \
	push pre-push do-push post-push

build: pre-build docker-build post-build  ## build the application image

pre-build:

post-build:

pre-push:

post-push:

docker-build: .release
	@if [ ! -f /usr/local/bin/docker-build.sh ] ; then \
		curl -s https://gitlab.com/ska-telescope/ska-k8s-tools/-/raw/master/docker/docker-builder/scripts/docker-build.sh -o docker-build.sh; \
		chmod +x docker-build.sh; \
		PROJECT=$(PROJECT) \
		DOCKER_REGISTRY_HOST=$(CAR_OCI_REGISTRY_HOST) \
		DOCKER_REGISTRY_USER=$(CAR_OCI_REGISTRY_PREFIX) \
		DOCKER_BUILD_CONTEXT=$(BUILD_CONTEXT) \
		DOCKER_FILE_PATH=$(FILE_PATH) \
		VERSION=$(VERSION) \
		TAG=$(TAG) \
		ADDITIONAL_ARGS="--build-arg http_proxy --build-arg https_proxy" \
		./docker-build.sh; status=$$?; rm docker-build.sh; \
		if [$$status != 0 ]; then \
			exit $$status; \
		fi; \
	else \
		PROJECT=$(PROJECT) \
		DOCKER_REGISTRY_HOST=$(CAR_OCI_REGISTRY_HOST) \
		DOCKER_REGISTRY_USER=$(CAR_OCI_REGISTRY_PREFIX) \
		DOCKER_BUILD_CONTEXT=$(BUILD_CONTEXT) \
		DOCKER_FILE_PATH=$(FILE_PATH) \
		VERSION=$(VERSION) \
		TAG=$(TAG) \
		ADDITIONAL_ARGS="--build-arg http_proxy --build-arg https_proxy" \
		/usr/local/bin/docker-build.sh; \
		if [$$? != 0 ]; then \
			exit $$?; \
		fi; \
	fi; 

.release:
	@echo "release=0.0.0" > .release
	@echo "tag=$(NAME)-0.0.0" >> .release
	@echo INFO: .release created
	@cat .release

release: check-status check-release build push

push: pre-push do-push post-push  ## push the image to the Docker registry

do-push:
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

snapshot: build push

showver: .release
	@. $(RELEASE_SUPPORT); getVersion

bump-patch-release: VERSION := $(shell . $(RELEASE_SUPPORT); nextPatchLevel)
bump-patch-release: .release tag

bump-minor-release: VERSION := $(shell . $(RELEASE_SUPPORT); nextMinorLevel)
bump-minor-release: .release tag

bump-major-release: VERSION := $(shell . $(RELEASE_SUPPORT); nextMajorLevel)
bump-major-release: .release tag

patch-release: tag-patch-release release
	@echo $(VERSION)

minor-release: tag-minor-release release
	@echo $(VERSION)

major-release: tag-major-release release
	@echo $(VERSION)

tag: TAG=$(shell . $(RELEASE_SUPPORT); getTag $(VERSION))
tag: check-status
#	@. $(RELEASE_SUPPORT) ; ! tagExists $(TAG) || (echo "ERROR: tag $(TAG) for version $(VERSION) already tagged in git" >&2 && exit 1) ;
	@. $(RELEASE_SUPPORT) ; setRelease $(VERSION)
#	git add .
#	git commit -m "bumped to version $(VERSION)" ;
#	git tag $(TAG) ;
#	@ if [ -n "$(shell git remote -v)" ] ; then git push --tags ; else echo 'no remote to push tags to' ; fi

check-status:
	@. $(RELEASE_SUPPORT) ; ! hasChanges || (echo "ERROR: there are still outstanding changes" >&2 && exit 1) ;

check-release: .release
	@. $(RELEASE_SUPPORT) ; tagExists $(TAG) || (echo "ERROR: version not yet tagged in git. make [minor,major,patch]-release." >&2 && exit 1) ;
	@. $(RELEASE_SUPPORT) ; ! differsFromRelease $(TAG) || (echo "ERROR: current directory differs from tagged $(TAG). make [minor,major,patch]-release." ; exit 1)

