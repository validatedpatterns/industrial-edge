.PHONY: default
default: show

.PHONY: help
# No need to add a comment here as help is described in common/
##@ Pattern tasks

help:
	@make -f common/Makefile MAKEFILE_LIST="Makefile common/Makefile" help

%:
	make -f common/Makefile $*

.PHONY: install
install: operator-deploy post-install ## installs the pattern, inits the vault and loads the secrets
	@echo "Installed"

.PHONY: post-install
post-install: ## Post-install tasks
	make load-secrets
	@echo "Done"

.PHONY: check-pipeline-resources
check-pipeline-resources: ## wait for all seed resources to be present
	scripts/check-pipeline-resources.sh

.PHONY: seed
seed: check-pipeline-resources ## run the seed pipeline (build all component, push to all env, no pr)
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

.PHONY: build-and-test-iot-consumer
build-and-test-iot-consumer: ## run iot consumer pipeline (build, test, push to manuela-tst-all, pr for prod)
	oc create -f charts/datacenter/pipelines/extra/build-and-test-iot-consumer.yaml

.PHONY: build-and-test-iot-frontend
build-and-test-iot-frontend: ## run iot frontend pipeline (build, test, push to manuela-tst-all, pr for prod)
	oc create -f charts/datacenter/pipelines/extra/build-and-test-iot-frontend.yaml

.PHONY: build-and-test-iot-software-sensor
build-and-test-iot-software-sensor: ## run iot software-sensor pipeline (build, test, push to manuela-tst-all, pr for prod)
	oc create -f charts/datacenter/pipelines/extra/build-and-test-iot-software-sensor.yaml
