HELM_HOST ?= https://nexus.engageska-portugal.pt## helm host url https
MINIKUBE ?= true## Minikube or not
MARK ?= all
IMAGE_TO_TEST ?= $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):latest## docker image that will be run for testing purpose
TANGO_HOST=$(shell helm get values ${RELEASE_NAME} -a -n ${KUBE_NAMESPACE} | grep tango_host | head -1 | cut -d':' -f2 | cut -d' ' -f2):10000

CHART_TO_PUB ?= tango-example## list of charts to be published on gitlab -- umbrella charts for testing purpose

CI_PROJECT_PATH_SLUG ?= tango-example
CI_ENVIRONMENT_SLUG ?= tango-example

.DEFAULT_GOAL := help

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
	@kubectl describe namespace $(KUBE_NAMESPACE) > /dev/null 2>&1 ; \
		K_DESC=$$? ; \
		if [ $$K_DESC -eq 0 ] ; \
		then kubectl describe namespace $(KUBE_NAMESPACE); \
		else kubectl create namespace $(KUBE_NAMESPACE); \
		fi

delete_namespace: ## delete the kubernetes namespace
	@if [ "default" == "$(KUBE_NAMESPACE)" ] || [ "kube-system" == "$(KUBE_NAMESPACE)" ]; then \
	echo "You cannot delete Namespace: $(KUBE_NAMESPACE)"; \
	exit 1; \
	else \
	kubectl describe namespace $(KUBE_NAMESPACE) && kubectl delete namespace $(KUBE_NAMESPACE); \
	fi

package: ## package charts
	@echo "Packaging helm charts. Any existing file won't be overwritten."; \
	mkdir -p ../tmp
	@for i in $(CHART_TO_PUB); do \
	helm package $${i} --destination ../tmp > /dev/null; \
	done; \
	mkdir -p ../repository && cp -n ../tmp/* ../repository; \
	cd ../repository && helm repo index .; \
	rm -rf ../tmp

install-chart: namespace## install the helm chart with name RELEASE_NAME and path UMBRELLA_CHART_PATH on the namespace KUBE_NAMESPACE 
	@sed -e 's/CI_PROJECT_PATH_SLUG/$(CI_PROJECT_PATH_SLUG)/' $(UMBRELLA_CHART_PATH)values.yaml > generated_values.yaml; \
	sed -e 's/CI_ENVIRONMENT_SLUG/$(CI_ENVIRONMENT_SLUG)/' generated_values.yaml > values.yaml; \
	helm dependency update $(UMBRELLA_CHART_PATH); \
	helm install $(RELEASE_NAME) \
	--set minikube=$(MINIKUBE) \
	--values values.yaml \
	 $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE); \
	 rm generated_values.yaml; \
	 rm values.yaml

uninstall-chart: ## uninstall the ska-docker helm chart on the namespace ska-docker
	helm template  $(RELEASE_NAME) $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE)  | kubectl delete -f - ; \
	helm uninstall  $(RELEASE_NAME) --namespace $(KUBE_NAMESPACE) 

reinstall-chart: uninstall-chart install-chart ## reinstall the ska-docker helm chart on the namespace ska-docker

upgrade-chart: ## upgrade the ska-docker helm chart on the namespace ska-docker
	helm upgrade --set minikube=$(MINIKUBE) $(RELEASE_NAME) $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE) 

wait:## wait for pods to be ready
	@echo "Waiting for pods to be ready"
	@date
	@kubectl -n $(KUBE_NAMESPACE) get pods
	@jobs=$$(kubectl get job --output=jsonpath={.items..metadata.name} -n $(KUBE_NAMESPACE)); kubectl wait job --for=condition=complete --timeout=120s $$jobs -n $(KUBE_NAMESPACE)
	@kubectl -n $(KUBE_NAMESPACE) wait --for=condition=ready -l app=ska-docker --timeout=120s pods || exit 1
	@date

show: ## show the helm chart
	@helm $(HELM_RELEASE) charts/$(HELM_CHART)/ \
		--namespace $(KUBE_NAMESPACE) \
		--set xauthority="$(XAUTHORITYx)" \
		--set display="$(DISPLAY)" 

chart_lint: ## lint check the helm chart
	@helm lint $(UMBRELLA_CHART_PATH) \
		--namespace $(KUBE_NAMESPACE) 

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

# Utility target to install Helm dependencies
helm_dependencies:
	@which helm ; rc=$$?; \
	if [[ $$rc != 0 ]]; then \
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3; \
	chmod 700 get_helm.sh; \
	./get_helm.sh; \
	fi; \
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
	@KUBE_CONFIG_BASE64=`kubectl config view --flatten | base64`; \
	echo "KUBE_CONFIG_BASE64: $$(echo $${KUBE_CONFIG_BASE64} | cut -c 1-40)..."; \
	echo "appended to: PrivateRules.mak"; \
	echo -e "\n\n# base64 encoded from: kubectl config view --flatten\nKUBE_CONFIG_BASE64 = $${KUBE_CONFIG_BASE64}" >> PrivateRules.mak

#
# defines a function to copy the ./post-deployment directory into the K8s TEST_RUNNER
# and then runs the requested make target in the container.
# capture the output of the test in a tar file
# stream the tar file base64 encoded to the Pod logs
# 
k8s_test = tar -c post-deployment/ | \
		kubectl run $(TEST_RUNNER) \
		--namespace $(KUBE_NAMESPACE) -i --wait --restart=Never \
		--image-pull-policy=IfNotPresent \
		--image=$(IMAGE_TO_TEST) -- \
		/bin/bash -c "mkdir testing && tar xv --directory testing --strip-components 1 --warning=all && cd testing && \
		make KUBE_NAMESPACE=$(KUBE_NAMESPACE) HELM_RELEASE=$(RELEASE_NAME) TANGO_HOST=$(TANGO_HOST) MARK=$(MARK) $1 && \
		tar -czvf /tmp/test-results.tgz build && \
		echo '~~~~BOUNDARY~~~~' && \
		cat /tmp/test-results.tgz | base64 && \
		echo '~~~~BOUNDARY~~~~'" \
		2>&1

# run the test function
# save the status
# clean out charts/build dir
# print the logs minus the base64 encoded payload
# pull out the base64 payload and unpack to charts/build/ dir
# base64 payload is given a boundary "~~~~BOUNDARY~~~~" and extracted using perl
# clean up the run to completion container
# exit the saved status
test: ## test the application on K8s
	$(call k8s_test,test); \
		status=$$?; \
		rm-rf charts/build; \
		kubectl --namespace $(KUBE_NAMESPACE) logs $(TEST_RUNNER) | \
		perl -ne 'BEGIN {$$on=0;}; if (index($$_, "~~~~BOUNDARY~~~~")!=-1){$$on+=1;next;}; print if $$on % 2;' | \
		base64 -d | tar -xzf - --directory charts; \
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


helm_tests:  ## run Helm chart tests 
	helm test $(HELM_RELEASE) --cleanup

help:  ## show this help.
	@echo "make targets:"
	@grep -hE '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""; echo "make vars (+defaults):"
	@grep -hE '^[0-9a-zA-Z_-]+ \?=.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = " \?\= "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\#\#/  \#/'

smoketest: ## check that the number of waiting containers is zero (10 attempts, wait time 30s).
	@echo "Smoke test START"; \
	n=10; \
	while [ $$n -gt 0 ]; do \
		waiting=`kubectl get pods -n $(KUBE_NAMESPACE) -o=jsonpath='{.items[*].status.containerStatuses[*].state.waiting.reason}' | wc -w`; \
		echo "Waiting containers=$$waiting"; \
		if [ $$waiting -ne 0 ]; then \
			echo "Waiting 30s for pods to become running...#$$n"; \
			sleep 30s; \
		fi; \
		if [ $$waiting -eq 0 ]; then \
			echo "Smoke test SUCCESS"; \
			exit 0; \
		fi; \
		if [ $$n -eq 1 ]; then \
			waiting=`kubectl get pods -n $(KUBE_NAMESPACE) -o=jsonpath='{.items[*].status.containerStatuses[*].state.waiting.reason}' | wc -w`; \
			echo "Smoke test FAILS"; \
			echo "Found $$waiting waiting containers: "; \
			kubectl get pods -n $(KUBE_NAMESPACE) -o=jsonpath='{range .items[*].status.containerStatuses[?(.state.waiting)]}{.state.waiting.message}{"\n"}{end}'; \
			exit 1; \
		fi; \
		n=`expr $$n - 1`; \
	done
