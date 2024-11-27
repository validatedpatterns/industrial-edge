import logging
import os
import re
import subprocess

import pytest

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.check_logging_hub
def test_check_logging_hub():
    logger.info("Checking logs for machine-sensor-1 in manuela-tst-all namespace")
    app_string = "app=machine-sensor-1"
    log_out = get_log_output(app_string, namespace="manuela-tst-all")
    search_terms = ["Current", "Measure", "vibration"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in machine-sensor-1 log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in machine-sensor-1 log")

    logger.info("Checking logs for machine-sensor-2 in manuela-tst-all namespace")
    app_string = "app=machine-sensor-2"
    log_out = get_log_output(app_string, namespace="manuela-tst-all")
    search_terms = ["Current", "Measure", "vibration"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in machine-sensor-2 log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in machine-sensor-2 log")

    logger.info("Checking logs for messaging in manuela-tst-all namespace")
    app_string = "app=messaging"
    log_out = get_log_output(app_string, namespace="manuela-tst-all")
    search_terms = ["handleVibration", "Anomaly"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in messaging log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in messaging log")

    logger.info(
        "Checking logs for anomaly-detection-predictor in manuela-tst-all" " namespace"
    )
    app_string = "modelmesh-service=modelmesh-serving"
    log_out = get_log_output(
        app_string, namespace="manuela-tst-all", container="mlserver"
    )
    search_terms = ["/inference.GRPCInferenceService/ModelInfer"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in anomaly-detection-predictor log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in anomaly-detection-predictor log")

    logger.info("Checking logs for kafka-integration in manuela-tst-all namespace")
    app_string = "camel.apache.org/integration=mqtt2kafka-integration"
    log_out = get_log_output(app_string, namespace="manuela-tst-all")
    search_terms = ["temperature", "vibration"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in kafka-integration log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in kafka-integration log")


def get_log_output(app_string, namespace, container=None):
    if container is None:
        cmd_out = subprocess.run(
            [oc, "logs", "-l", app_string, "--since=10s", "-n", namespace],
            capture_output=True,
        )
    else:
        cmd_out = subprocess.run(
            [
                oc,
                "logs",
                "-l",
                app_string,
                "-c",
                container,
                "--since=10s",
                "-n",
                namespace,
            ],
            capture_output=True,
        )

    logger.info(cmd_out)

    if cmd_out.stdout:
        cmd_out = cmd_out.stdout.decode("utf-8")
        return cmd_out
    else:
        logger.error(f"FAIL: {cmd_out.stderr}")
        assert False, cmd_out.stderr


def search_log_output(log, search):
    for term in search:
        if not re.search(term, log):
            return False
    return True
