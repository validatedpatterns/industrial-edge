BOOTSTRAP=1
ARGO_TARGET_NAMESPACE=manuela-ci

.PHONY: default
default: show

%:
	make -f common/Makefile $*

install: deploy
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret
	make sleep-seed
endif

secret:
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret

sleep-seed:
	while [ 1 ]; do make seed 1>/dev/null 2>/dev/null && echo "Bootstrap seed running" && break; sleep 5; done

seed:
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml
