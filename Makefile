BOOTSTRAP=1
ARGO_TARGET_NAMESPACE=manuela-ci

.PHONY: default
default: show

%:
	make -f common/Makefile $*

install: deploy
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret
	make seed
endif

secret:
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret

seed:
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml
