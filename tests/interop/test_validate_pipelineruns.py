import logging
import os

import pytest
from validatedpatterns_tests.interop import components

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_pipelineruns
def test_validate_pipelineruns(openshift_dyn_client):
    logger.info("Checking Openshift pipelines")
    project = "manuela-ci"

    expected_pipelines = [
        "seed",
        "build-and-test-iot-consumer",
        "build-and-test-iot-frontend",
        "build-and-test-iot-software-sensor",
    ]

    expected_pipelineruns = [
        "seed-run",
    ]

    err_msg = components.validate_pipelineruns(
        openshift_dyn_client, project, expected_pipelines, expected_pipelineruns
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pipeline verification succeeded.")
