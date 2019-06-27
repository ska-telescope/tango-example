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
  DOCKER_REGISTRY_USER = tango-example
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
	docker build $(DOCKER_BUILD_ARGS) -t $(IMAGE):$(VERSION) $(DOCKER_BUILD_CONTEXT) -f $(DOCKER_FILE_PATH) --build-arg DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) --build-arg DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER)
	@DOCKER_MAJOR=$(shell docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f1) ; \
	DOCKER_MINOR=$(shell docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f2) ; \
	if [ $$DOCKER_MAJOR -eq 1 ] && [ $$DOCKER_MINOR -lt 10 ] ; then \
		echo docker tag -f $(IMAGE):$(VERSION) $(IMAGE):latest ;\
		docker tag -f $(IMAGE):$(VERSION) $(IMAGE):latest ;\
	else \
		echo docker tag $(IMAGE):$(VERSION) $(IMAGE):latest ;\
		docker tag $(IMAGE):$(VERSION) $(IMAGE):latest ; \
	fi

.release:
	@echo "release=0.0.0" > .release
	@echo "tag=$(NAME)-0.0.0" >> .release
	@echo INFO: .release created
	@cat .release

release: check-status check-release build push

push: pre-push do-push post-push  ## push the image to the Docker registry

do-push:
#	docker push $(IMAGE):$(VERSION)
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

k8s: ## Which kubernetes are we connected to
	@echo "Kubernetes cluster-info:"
	@kubectl cluster-info
	@echo ""
	@echo "kubectl version:"
	@kubectl version
	@echo ""
	@echo "Helm version:"
	@helm version --client

namespace: ## create the kubernetes namespace
	kubectl describe namespace $(KUBE_NAMESPACE) || kubectl create namespace $(KUBE_NAMESPACE)

delete_namespace: ## delete the kubernetes namespace
	@if [ "default" == "$(KUBE_NAMESPACE)" ] || [ "kube-system" == "$(KUBE_NAMESPACE)" ]; then \
	echo "You cannot delete Namespace: $(KUBE_NAMESPACE)"; \
	exit 1; \
	else \
	kubectl describe namespace $(KUBE_NAMESPACE) && kubectl delete namespace $(KUBE_NAMESPACE); \
	fi

deploy: namespace mkcerts  ## deploy the helm chart (without Tiller)
	@helm template charts/$(HELM_CHART)/ --name $(HELM_RELEASE) \
		--namespace $(KUBE_NAMESPACE) \
    --tiller-namespace $(KUBE_NAMESPACE) \
		--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" \
		--set ingress.hostname=$(INGRESS_HOST) \
		--set helmTests=false \
		 | kubectl -n $(KUBE_NAMESPACE) apply -f -

install: namespace mkcerts  ## install the helm chart (with Tiller)
	@helm tiller run $(KUBE_NAMESPACE) -- helm install charts/$(HELM_CHART)/ --name $(HELM_RELEASE) \
		--wait \
		--namespace $(KUBE_NAMESPACE) \
		--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" \
    --tiller-namespace $(KUBE_NAMESPACE) \
		--set ingress.hostname=$(INGRESS_HOST)

show: mkcerts ## show the helm chart
	@helm template charts/$(HELM_CHART)/ --name $(HELM_RELEASE) \
		--namespace $(KUBE_NAMESPACE) \
    --tiller-namespace $(KUBE_NAMESPACE) \
	--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" \
		--set ingress.hostname=$(INGRESS_HOST)

lint: ## lint check the helm chart
	@helm lint charts/$(HELM_CHART)/ \
		--namespace $(KUBE_NAMESPACE) \
    --tiller-namespace $(KUBE_NAMESPACE) \
		--set ingress.hostname=$(INGRESS_HOST)
		--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" \

delete: ## delete the helm chart release (without Tiller)
	@helm template charts/$(HELM_CHART)/ --name $(HELM_RELEASE) \
		--namespace $(KUBE_NAMESPACE) \
    --tiller-namespace $(KUBE_NAMESPACE) \
	--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" \
		--set ingress.hostname=$(INGRESS_HOST) \
		--set helmTests=false \
  | kubectl -n $(KUBE_NAMESPACE) delete -f -

helm_delete: ## delete the helm chart release (with Tiller)
	@helm tiller run $(KUBE_NAMESPACE) -- helm delete $(HELM_RELEASE) --purge \
    --tiller-namespace $(KUBE_NAMESPACE)

describe: ## describe Pods executed from Helm chart
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l app.kubernetes.io/instance=$(HELM_RELEASE) -o=name`; \
	do echo "---------------------------------------------------"; \
	echo "Describe for $${i}"; \
	echo kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	echo ""; echo ""; echo ""; \
	done

logs: ## show Helm chart POD logs
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l app.kubernetes.io/instance=$(HELM_RELEASE) -o=name`; \
	do \
	echo "---------------------------------------------------"; \
	echo "Logs for $${i}"; \
	echo kubectl -n $(KUBE_NAMESPACE) logs $${i}; \
	echo kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.initContainers[*].name}"; \
	echo "---------------------------------------------------"; \
	for j in `kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.initContainers[*].name}"`; do \
	RES=`kubectl -n $(KUBE_NAMESPACE) logs $${i} -c $${j} 2>/dev/null`; \
	echo "initContainer: $${j}"; echo "$${RES}"; \
	echo "---------------------------------------------------";\
	done; \
	echo "Main Pod logs for $${i}"; \
	echo "---------------------------------------------------"; \
	for j in `kubectl -n $(KUBE_NAMESPACE) get $${i} -o jsonpath="{.spec.containers[*].name}"`; do \
	RES=`kubectl -n $(KUBE_NAMESPACE) logs $${i} -c $${j} 2>/dev/null`; \
	echo "Container: $${j}"; echo "$${RES}"; \
	echo "---------------------------------------------------";\
	done; \
	echo "---------------------------------------------------"; \
	echo ""; echo ""; echo ""; \
	done

localip:  ## set local Minikube IP in /etc/hosts file for Ingress $(INGRESS_HOST)
	@new_ip=`minikube ip` && \
	existing_ip=`grep $(INGRESS_HOST) /etc/hosts || true` && \
	echo "New IP is: $${new_ip}" && \
	echo "Existing IP: $${existing_ip}" && \
	if [ -z "$${existing_ip}" ]; then echo "$${new_ip} $(INGRESS_HOST)" | sudo tee -a /etc/hosts; \
	else sudo perl -i -ne "s/\d+\.\d+.\d+\.\d+/$${new_ip}/ if /$(INGRESS_HOST)/; print" /etc/hosts; fi && \
	echo "/etc/hosts is now: " `grep $(INGRESS_HOST) /etc/hosts`

mkcerts:  ## Make dummy certificates for $(INGRESS_HOST) and Ingress
	@if [ ! -f charts/$(HELM_CHART)/secrets/tls.key ]; then \
	openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
	   -keyout charts/$(HELM_CHART)/secrets/tls.key \
		 -out charts/$(HELM_CHART)/secrets/tls.crt \
		 -subj "/CN=$(INGRESS_HOST)/O=Minikube"; \
	else \
	echo "SSL cert already exits in charts/$(HELM_CHART)/secrets ... skipping"; \
	fi

# Utility target to install Helm dependencies
helm_dependencies:
	@which helm ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
	curl "https://kubernetes-helm.storage.googleapis.com/helm-$(HELM_VERSION)-linux-amd64.tar.gz" | tar zx; \
	mv linux-amd64/helm /usr/bin/; \
	helm init --client-only; \
	fi
	@helm init --client-only
	@if [ ! -d $$HOME/.helm/plugins/helm-tiller ]; then \
	echo "installing tiller plugin..."; \
	helm plugin install https://github.com/rimusz/helm-tiller; \
	fi
	helm version --client
	@helm tiller stop 2>/dev/null || true

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
