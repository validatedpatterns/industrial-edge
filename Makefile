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

.ONESHELL:
SHELL = bash
sleep-seed:
	while [ 1 ]; do 
		echo "Waiting for seed resources to be ready in manuela-ci"
		oc get -n manuela-ci pipeline seed 1>/dev/null 2>/dev/null && \
		oc get -n manuela-ci task tkn 1>/dev/null 2>/dev/null && \
		make seed 1>/dev/null 2>/dev/null && \
		echo "Bootstrap seed now running" && break; 
		sleep 5;
	done

seed:
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

build-and-test:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run.yaml
