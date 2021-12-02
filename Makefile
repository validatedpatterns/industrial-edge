BOOTSTRAP=1
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"
TARGET_REPO=$(shell git remote show origin | grep Push | sed -e 's/.*URL://' -e 's%:[a-z].*@%@%' -e 's%:%/%' -e 's%git@%https://%' )
CHART_OPTS=-f common/examples/values-secret.yaml -f values-global.yaml -f values-datacenter.yaml --set global.targetRevision=main --set global.valuesDirectoryURL="https://github.com/pattern-clone/pattern/raw/main/" --set global.pattern="industrial-edge" --set global.namespace="pattern-namespace"
TESTDIR=tests
TEST_VARIANT=normal

.PHONY: default
default: show

%:
	echo "Delegating $* target"
	make -f common/Makefile $*

install: deploy
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

CHARTS=$(wildcard charts/*/*)

tests:
	@for t in $(CHARTS); do scripts/test.sh $$t naked ""; if [ $$? != 0 ]; then exit 1; fi; done
	@for t in $(CHARTS); do scripts/test.sh $$t normal "$(CHART_OPTS)"; if [ $$? != 0 ]; then exit 1; fi; done

