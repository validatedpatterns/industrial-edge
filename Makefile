NAME=$(shell basename `pwd`)
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"
TARGET_BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
HUBCLUSTER_APPS_DOMAIN=$(shell oc get ingresses.config/cluster -o jsonpath={.spec.domain})
TARGET_ORIGIN ?= origin
TARGET_REPO=$(shell git ls-remote --get-url --symref $(TARGET_ORIGIN) | sed -e 's/.*URL:[[:space:]]*//' -e 's%^git@%%' -e 's%^https://%%' -e 's%:%/%' -e 's%^%https://%')
CHART_OPTS=-f common/examples/values-secret.yaml -f values-global.yaml -f values-datacenter.yaml --set global.targetRevision=main --set global.valuesDirectoryURL="https://github.com/pattern-clone/pattern/raw/main/" --set global.pattern="industrial-edge" --set global.namespace="pattern-namespace"
HELM_OPTS=-f values-global.yaml --set main.git.repoURL="$(TARGET_REPO)" --set main.git.revision=$(TARGET_BRANCH) --set global.hubClusterDomain=$(HUBCLUSTER_APPS_DOMAIN)

.PHONY: default
default: show

.PHONY: help
# No need to add a comment here as help is described in common/
##@ Pattern tasks

help:
	@make -f common/Makefile MAKEFILE_LIST="Makefile common/Makefile" help

%:
	make -f common/Makefile $*

install: operator-deploy post-install ## installs the pattern, inits the vault and loads the secrets
	@echo "Installed"

post-install: ## Post-install tasks
	make load-secrets
	make argosecret
	@echo "Done"

sleep: ## waits for all seed resources to be presents
	scripts/sleep-seed.sh

sleep-seed: sleep seed ## waits for seed resources and calls seed-run
	true

seed: sleep ## waits for all seed resources
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

#  Makefiles that use this target must provide:
#  	PATTERN: The name of the pattern that is using it.  This will be used programmatically for the source namespace
#  	TARGET_NAMESPACE: target namespace to install the secret into
#  	COMPONENT: The component of the target namespace.  In industrial edge, factory or datacenter - and for the secret
#  		it needs to be datacenter because that's where the CI components run.
#  	SECRET_NAME: The name of the secret to manage
argosecret: ## creates the argo secret
	PATTERN="$(PATTERN)" TARGET_NAMESPACE="$(ARGO_TARGET_NAMESPACE)" COMPONENT="$(COMPONENT)" SECRET_NAME="$(SECRET_NAME)" scripts/secret.sh

build-and-test: ## run a build and test pipeline
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run.yaml

just-pr: ## run a build and test pipeline
	oc create -f charts/datacenter/pipelines/extra/just-pr-run.yaml

build-and-test-iot-anomaly-detection: ## run a build and test pipeline iot anomaly detection
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-anomaly-detection.yaml

build-and-test-iot-consumer: ## run a build and test pipeline iot consumer
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-consumer.yaml
