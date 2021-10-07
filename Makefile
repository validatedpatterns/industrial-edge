BOOTSTRAP=1
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"

.PHONY: default
default: show

%:
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
