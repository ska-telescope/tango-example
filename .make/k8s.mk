HELM_HOST ?= https://nexus.engageska-portugal.pt## helm host url https
MINIKUBE ?= true## Minikube or not
MARK ?= all## mark tests to be executed
FILE ?= ##this variable allow to execution of a single file in the pytest 
IMAGE_TO_TEST ?= $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):$(VERSION)## docker image that will be run for testing purpose
TANGO_HOST ?= tango-host-databaseds-from-makefile-$(RELEASE_NAME):10000## TANGO_HOST is an input!
LINTING_OUTPUT=$(shell helm lint charts/* | grep ERROR -c | tail -1)

CHARTS ?= event-generator tango-example test-parent## list of charts
KUBE_APP ?= tango-example

SLEEPTIME ?= 20
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

clean: ## clean out temp files
	@rm -rf ./charts/*/charts/*.tgz \
		./charts/*/Chart.lock \
		./charts/*/requirements.lock \
		./repository/* \
		./.eggs \
		./charts/build \
		./build \
		./docs/build \
		./dist \
		./tango_example.egg-info \
		tests/.pytest_cache \
		tests/unit/__pycache__ \
		tests/__pycache__ \
		tests/*/__pycache__ \
		src/ska_tango_examples/__pycache__ \
		src/ska_tango_examples/*/__pycache__ \
		.pytest_cache \
		.coverage


dep-up: ## update dependencies for every charts in the env var CHARTS
	@cd charts; \
	for i in $(CHARTS); do \
	echo "+++ Updating $${i} chart +++"; \
	helm dependency update $${i}; \
	done;

install-chart: clean dep-up namespace## install the helm chart with name RELEASE_NAME and path UMBRELLA_CHART_PATH on the namespace KUBE_NAMESPACE
	@helm upgrade --install $(RELEASE_NAME) \
	--set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set tango-base.display=$(DISPLAY) \
	--set tango-base.xauthority=$(XAUTHORITY) \
	--set tango_example.image.tag=$(VERSION) \
	--values gilab_values.yaml \
	 $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE); \
	 rm gilab_values.yaml

template-chart: clean dep-up## install the helm chart with name RELEASE_NAME and path UMBRELLA_CHART_PATH on the namespace KUBE_NAMESPACE
	@helm template $(RELEASE_NAME) \
	--set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set tango-base.display=$(DISPLAY) \
	--set tango-base.xauthority=$(XAUTHORITY) \
	--set tango_example.tango_example.image.tag=$(VERSION) \
	--set event_generator.events_generator.image.tag=$(VERSION) \
	--values gilab_values.yaml \
	--debug \
	 $(UMBRELLA_CHART_PATH) --namespace $(KUBE_NAMESPACE); \
	 rm gilab_values.yaml

bounce:
	echo "stopping ..."; \
	kubectl -n $(KUBE_NAMESPACE) scale --replicas=0 statefulset.apps -l app=$(KUBE_APP); \
	echo "starting ..."; \
	kubectl -n $(KUBE_NAMESPACE) scale --replicas=1 statefulset.apps -l app=$(KUBE_APP); \
	echo "WARN: 'make wait' for terminating pods not possible. Use 'make watch'"

uninstall-chart: ## uninstall the test-parent helm chart on the namespace tango-example
	@helm uninstall  $(RELEASE_NAME) --namespace $(KUBE_NAMESPACE) 

reinstall-chart: uninstall-chart install-chart ## reinstall test-parent helm chart on the namespace tango-example

upgrade-chart: install-chart ## upgrade the test-parent helm chart on the namespace tango-example

wait: # wait for pods to be ready
	@echo "Waiting for pods to be ready"
	@date
	@kubectl -n $(KUBE_NAMESPACE) get pods
	@date
	@jobs=$$(kubectl get job --output=jsonpath={.items..metadata.name} -n $(KUBE_NAMESPACE)); kubectl wait job --for=condition=complete --timeout=120s $$jobs -n $(KUBE_NAMESPACE)
	@date
	@kubectl -n $(KUBE_NAMESPACE) wait --for=condition=ready -l app=$(KUBE_APP) --timeout=120s pods || exit 1
	@date

watch:
	watch kubectl get all,pv,pvc,ingress -n $(KUBE_NAMESPACE)

# chart_lint: dep-up ## lint check the helm chart
chart_lint: dep-up ## lint check the helm chart
	@mkdir -p charts/test-parent/templates;
	@mkdir -p build/reports; \
	helm lint charts/* --with-subcharts; \
	echo "<testsuites><testsuite errors=\"$(LINTING_OUTPUT)\" failures=\"0\" name=\"helm-lint\" skipped=\"0\" tests=\"0\" time=\"0.000\" timestamp=\"$(shell date)\"> </testsuite> </testsuites>" > build/reports/linting-charts.xml
	exit $(LINTING_OUTPUT)

describe: ## describe Pods executed from Helm chart
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l app=$(KUBE_APP) -o=name`; \
	do echo "---------------------------------------------------"; \
	echo "Describe for $${i}"; \
	echo kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	kubectl -n $(KUBE_NAMESPACE) describe $${i}; \
	echo "---------------------------------------------------"; \
	echo ""; echo ""; echo ""; \
	done

logs: ## show Helm chart POD logs
	@for i in `kubectl -n $(KUBE_NAMESPACE) get pods -l app=$(KUBE_APP) -o=name`; \
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
k8s_test = tar -c tests/ | \
		kubectl run $(TEST_RUNNER) \
		--namespace $(KUBE_NAMESPACE) -i --wait --restart=Never \
		--image-pull-policy=IfNotPresent \
		--image=$(IMAGE_TO_TEST) -- \
		/bin/bash -c "mkdir -p build; tar xv --directory tests --strip-components 1 --warning=all; pip install -r tests/requirements.txt; \
		PYTHONPATH=/app/src:/app/src/ska_tango-examples KUBE_NAMESPACE=$(KUBE_NAMESPACE) HELM_RELEASE=$(RELEASE_NAME) TANGO_HOST=$(TANGO_HOST) \
		pytest $(if $(findstring all,$(MARK)),, -m $(MARK)) --true-context $(FILE) && \
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
	$(call k8s_test); \
		status=$$?; \
		rm -rf charts/build; \
		kubectl --namespace $(KUBE_NAMESPACE) logs $(TEST_RUNNER) | \
		perl -ne 'BEGIN {$$on=0;}; if (index($$_, "~~~~BOUNDARY~~~~")!=-1){$$on+=1;next;}; print if $$on % 2;' | \
		base64 -d | tar -xzf - --directory charts; \
		kubectl --namespace $(KUBE_NAMESPACE) delete pod $(TEST_RUNNER); \
		exit $$status

help: # show this help.
	@echo "make targets:"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ": .*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""; echo "make vars (+defaults):"
	@grep -E '^[0-9a-zA-Z_-]+ \?=.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = " \\?= "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

smoketest: wait # wait target
