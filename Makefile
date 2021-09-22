BOOTSTRAP=1
ARGO_TARGET_NAMESPACE=manuela-ci

show:
	make -f common/Makefile show

init:
	make -f common/Makefile init

deploy:
	make -f common/Makefile deploy
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret
endif

upgrade:
	make -f common/Makefile upgrade
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) argosecret
endif

uninstall:
	make -f common/Makefile uninstall

.phony: install
