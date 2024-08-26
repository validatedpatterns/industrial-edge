#!/usr/bin/bash

export EXTERNAL_TEST="true"
export PATTERN_NAME="IndustrialEdge"
export PATTERN_SHORTNAME="industrialedge"

if [ -z "${KUBECONFIG}" ]; then
    echo "No kubeconfig file set for hub cluster"
    exit 1
fi

if [ -z "${KUBECONFIG_EDGE}" ]; then
    echo "No kubeconfig file set for edge cluster"
    exit 1
fi

if [ -z "${INFRA_PROVIDER}" ]; then
    echo "INFRA_PROVIDER is not defined"
    exit 1
fi

if [ -z "${WORKSPACE}" ]; then
    export WORKSPACE=/tmp
fi

pytest -lv --disable-warnings test_subscription_status_hub.py --kubeconfig $KUBECONFIG --junit-xml $WORKSPACE/test_subscription_status_hub.xml

pytest -lv --disable-warnings test_subscription_status_edge.py --kubeconfig $KUBECONFIG_EDGE --junit-xml $WORKSPACE/test_subscription_status_edge.xml

pytest -lv --disable-warnings test_validate_hub_site_components.py --kubeconfig $KUBECONFIG --junit-xml $WORKSPACE/test_validate_hub_site_components.xml

pytest -lv --disable-warnings test_validate_edge_site_components.py --kubeconfig $KUBECONFIG_EDGE --junit-xml $WORKSPACE/test_validate_edge_site_components.xml

pytest -lv --disable-warnings test_validate_pipelineruns.py --kubeconfig $KUBECONFIG --junit-xml $WORKSPACE/test_validate_pipelineruns.xml

pytest -lv --disable-warnings test_check_logging_hub.py --kubeconfig $KUBECONFIG --junit-xml $WORKSPACE/test_check_logging_hub.xml

KUBECONFIG=$KUBECONFIG_EDGE pytest -lv --disable-warnings test_check_logging_edge.py --kubeconfig $KUBECONFIG_EDGE --junit-xml $WORKSPACE/test_check_logging_edge.xml

KUBECONFIG=$KUBECONFIG_EDGE pytest -lv --disable-warnings test_toggle_machine_sensor.py --kubeconfig $KUBECONFIG_EDGE --junit-xml $WORKSPACE/test_toggle_machine_sensor.xml

pytest -lv --disable-warnings test_pipeline_build_check.py --kubeconfig $KUBECONFIG --junit-xml $WORKSPACE/test_pipeline_build_check.xml

python3 create_ci_badge.py
