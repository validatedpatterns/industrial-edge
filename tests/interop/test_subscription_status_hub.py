import logging

import pytest
from validatedpatterns_tests.interop import subscription

from . import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.mark.subscription_status_hub
def test_subscription_status_hub(openshift_dyn_client):
    openshift_ver = subscription.openshift_version(openshift_dyn_client)
    openshift_ver = openshift_ver.instance.status.history[0].version
    if "4.17." in openshift_ver:
        # These are the operator subscriptions and their associated namespaces
        expected_subs = {
            "openshift-gitops-operator": ["openshift-operators"],
            "advanced-cluster-management": ["open-cluster-management"],
            "openshift-pipelines-operator-rh": ["openshift-operators"],
            "amq-broker-rhel8": ["manuela-tst-all"],
            "amq-streams": ["manuela-tst-all", "manuela-data-lake"],
            "camel-k": ["manuela-tst-all", "manuela-data-lake"],
            "rhods-operator": ["redhat-ods-operator"],
            "odf-operator": ["openshift-storage"],
            "odf-prometheus-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "odf-csi-addons-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "mcg-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "ocs-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "ocs-client-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "cephcsi-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "recipe-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "rook-ceph-operator-stable-4.17-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
        }

    elif "4.16." in openshift_ver:
        # These are the operator subscriptions and their associated namespaces
        expected_subs = {
            "openshift-gitops-operator": ["openshift-operators"],
            "advanced-cluster-management": ["open-cluster-management"],
            "openshift-pipelines-operator-rh": ["openshift-operators"],
            "amq-broker-rhel8": ["manuela-tst-all"],
            "amq-streams": ["manuela-tst-all", "manuela-data-lake"],
            "camel-k": ["manuela-tst-all", "manuela-data-lake"],
            "rhods-operator": ["redhat-ods-operator"],
            "odf-operator": ["openshift-storage"],
            "odf-prometheus-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "odf-csi-addons-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "mcg-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "ocs-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "ocs-client-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "recipe-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
            "rook-ceph-operator-stable-4.16-redhat-operators-openshift-marketplace": [
                "openshift-storage"
            ],
        }

    else:
        err_msg = f"Openshift version {openshift_ver} not supported"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    err_msg = subscription.subscription_status(  # pylint: disable=E1123
        openshift_dyn_client, expected_subs, diff=True
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Subscription status check passed")
