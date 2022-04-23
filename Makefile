NAME=$(shell basename `pwd`)
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"
SECRETS=~/values-secret.yaml
TARGET_BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
HUBCLUSTER_APPS_DOMAIN=$(shell oc get ingresses.config/cluster -o jsonpath={.spec.domain})
TARGET_REPO=$(shell git remote show origin | grep Push | sed -e 's/.*URL:[[:space:]]*//' -e 's%^git@%%' -e 's%^https://%%' -e 's%:%/%' -e 's%^%https://%')
CHART_OPTS=-f common/examples/values-secret.yaml -f values-global.yaml -f values-datacenter.yaml --set global.targetRevision=main --set global.valuesDirectoryURL="https://github.com/pattern-clone/pattern/raw/main/" --set global.pattern="industrial-edge" --set global.namespace="pattern-namespace"
HELM_OPTS=-f values-global.yaml -f $(SECRETS) --set main.git.repoURL="$(TARGET_REPO)" --set main.git.revision=$(TARGET_BRANCH) --set global.hubClusterDomain=$(HUBCLUSTER_APPS_DOMAIN)

.PHONY: default
default: show

.PHONY: help
# No need to add a comment here as help is described in common/
help:
	@printf "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) common/Makefile | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)\n"

%:
	echo "Delegating $* target"
	make -f common/Makefile $*

pipeline-setup: ## calls the helm pipeline-setup
	helm install $(NAME)-secrets charts/secrets/pipeline-setup $(HELM_OPTS)

install: pipeline-setup deploy ## installs the pattern, sets up the pipelines, inits the vault and loads the secrets
	make vault-init
	make load-secrets
	make argosecret
#	seed now optional!
#	make sleep-seed

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

common-test: ## runs helm tests in common/
	make -C common -f common/Makefile test

test:
	make -f common/Makefile CHARTS="$(wildcard charts/datacenter/*)" PATTERN_OPTS="-f values-datacenter.yaml" test
	make -f common/Makefile CHARTS="$(wildcard charts/factory/*)" PATTERN_OPTS="-f values-factory.yaml" test

.PHONY: kubeconform
KUBECONFORM_SKIP=-skip 'CustomResourceDefinition,Pipeline,Task'
kubeconform:
	make -f common/Makefile KUBECONFORM_SKIP="$(KUBECONFORM_SKIP)" CHARTS="$(wildcard charts/datacenter/*)" kubeconform
	make -f common/Makefile KUBECONFORM_SKIP="$(KUBECONFORM_SKIP)" CHARTS="$(wildcard charts/factory/*)" kubeconform

helmlint:
	@for t in "$(wildcard charts/datacenter/*)" "$(wildcard charts/factory/*)"; do helm lint $$t; if [ $$? != 0 ]; then exit 1; fi; done
