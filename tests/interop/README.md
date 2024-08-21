# Running tests

## Prerequisites

* Openshift clusters with industrial-edge pattern installed
* kubeconfig files for Openshift clusters
* fork of industrial-edge repository

## Steps

* install oc client at ~/oc_client/oc
* create python3 venv, clone fork of industrial-edge repository
* export KUBECONFIG=\<path to hub kubeconfig file>
* export KUBECONFIG_EDGE=\<path to edge kubeconfig file>
* export INFRA_PROVIDER=\<infra platform description>
* (optional) export WORKSPACE=\<dir to save test results to> (defaults to /tmp)
* cd industrial-edge/
* ./pattern.sh make seed (allow ~30 minutes for pipeline completion)
* cd tests/interop
* pip install -r requirements.txt
* ./run_tests.sh

## Results

* results .xml files will be placed at $WORKSPACE
* test logs will be placed at $WORKSPACE/.results/test_execution_logs/
* CI badge file will be placed at $WORKSPACE
