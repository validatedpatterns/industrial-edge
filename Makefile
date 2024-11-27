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
seed: check-pipeline-resources ## run the seed pipipeline (test and prod, no pr)
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

.PHONY: build-and-test-iot-anomaly-detection
build-and-test-iot-anomaly-detection: ## run a build and test pipeline iot anomaly detection
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-anomaly-detection.yaml

.PHONY: build-and-test-iot-consumer
build-and-test-iot-consumer: ## run a build and test pipeline iot consumer
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-consumer.yaml

.PHONY: build-and-test-iot-frontend
build-and-test-iot-frontend: ## run a build and test pipeline iot frontend
	oc create -f charts/datacenter/pipelines/extra/build-and-test-iot-frontend.yaml

.PHONY: build-and-test-iot-software-sensor
build-and-test-iot-software-sensor: ## run a build and test pipeline iot software-sensor
	oc create -f charts/datacenter/pipelines/extra/build-and-test-iot-software-sensor.yaml
