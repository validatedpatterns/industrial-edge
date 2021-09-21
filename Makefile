BOOTSTRAP=1

show:
	make -f common/Makefile show

init:
	make -f common/Makefile init

deploy:
	make -f common/Makefile deploy
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=manuela-ci argosecret
endif

upgrade:
	make -f common/Makefile upgrade
ifeq ($(BOOTSTRAP),1)
	make -f common/Makefile TARGET_NAMESPACE=manuela-ci argosecret
endif

uninstall:
	make -f common/Makefile uninstall

.phony: install
