BOOTSTRAP=1
NAME=$(shell basename `pwd`)
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"
SECRETS=~/values-secret.yaml
TARGET_BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
HUBCLUSTER_APPS_DOMAIN=$(shell oc get ingresses.config/cluster -o jsonpath={.spec.domain})
TARGET_REPO=$(shell git remote show origin | grep Push | sed -e 's/.*URL:[[:space:]]*//' -e 's%:[a-z].*@%@%' -e 's%:%/%' -e 's%git@%https://%' )
CHART_OPTS=-f common/examples/values-secret.yaml -f values-global.yaml -f values-datacenter.yaml --set global.targetRevision=main --set global.valuesDirectoryURL="https://github.com/pattern-clone/pattern/raw/main/" --set global.pattern="industrial-edge" --set global.namespace="pattern-namespace"
HELM_OPTS=-f values-global.yaml -f $(SECRETS) --set main.git.repoURL="$(TARGET_REPO)" --set main.git.revision=$(TARGET_BRANCH) --set main.options.bootstrap=$(BOOTSTRAP) --set global.hubClusterDomain=$(HUBCLUSTER_APPS_DOMAIN)

.PHONY: default
default: show-secrets show

%:
	echo "Delegating $* target"
	make -f common/Makefile $*

show-secrets:
	helm template charts/datacenter/secrets/ --name-template $(NAME)-secrets $(HELM_OPTS)

create-secrets:
ifeq ($(BOOTSTRAP),1)
	helm install $(NAME)-secrets charts/datacenter/secrets $(HELM_OPTS)
endif

install: create-secrets deploy
ifeq ($(BOOTSTRAP),1)
	make secret
	make sleep-seed
endif

secret:
	make -f common/Makefile \
		PATTERN=$(PATTERN) TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) \
		SECRET_NAME=$(SECRET_NAME) COMPONENT=$(COMPONENT) argosecret

sleep:
	scripts/sleep-seed.sh

sleep-seed: sleep seed
	true

seed:
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

build-and-test:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run.yaml

build-and-test-iot-anomaly-detection:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-anomaly-detection.yaml

build-and-test-iot-consumer:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-consumer.yaml

test:
	make -f common/Makefile CHARTS="$(wildcard charts/datacenter/*)" PATTERN_OPTS="-f values-datacenter.yaml" test
	make -f common/Makefile CHARTS="$(wildcard charts/factory/*)" PATTERN_OPTS="-f values-factory.yaml" test
