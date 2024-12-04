import logging
import os
import re
import subprocess

import pytest

from . import __loggername__

# from time import sleep


logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.check_logging_edge
def test_check_logging_edge():
    logger.info(
        "Checking logs for machine-sensor-1 in"
        " manuela-stormshift-machine-sensor namespace"
    )
    app_string = "app=machine-sensor-1"
    log_out = get_log_output(app_string, namespace="manuela-stormshift-machine-sensor")
    search_terms = ["Current", "Measure", "vibration"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in machine-sensor-1 log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in machine-sensor-1 log")

    logger.info("Checking logs for messaging in manuela-stormshift-messaging namespace")
    app_string = "app=messaging"
    log_out = get_log_output(app_string, namespace="manuela-stormshift-messaging")
    search_terms = ["handleVibration", "Anomaly"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in messaging log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in messaging log")

    logger.info(
        "Checking logs for kafka (list) in manuela-stormshift-messaging" " namespace"
    )
    log_out = subprocess.run(
        [
            oc,
            "exec",
            "factory-kafka-cluster-kafka-0",
            "-c",
            "kafka",
            "-n",
            "manuela-stormshift-messaging",
            "--",
            "bin/kafka-topics.sh",
            "--list",
            "--bootstrap-server",
            "factory-kafka-cluster-kafka-bootstrap:9092",
        ],
        capture_output=True,
    )
    log_out = log_out.stdout.decode("utf-8")
    search_terms = ["temperature", "vibration"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find expected output in kafka output"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found expected output in kafka log")

    # logger.info(
    #     "Checking logs for kafka (iot-sensor-sw-temperature) in"
    #     " manuela-stormshift-messaging namespace"
    # )
    # log_proc = subprocess.Popen(
    #     [
    #         oc,
    #         "exec",
    #         "factory-kafka-cluster-kafka-0",
    #         "-c",
    #         "kafka",
    #         "-n",
    #         "manuela-stormshift-messaging",
    #         "--",
    #         "bin/kafka-console-consumer.sh",
    #         "--topic",
    #         "manuela-factory.iot-sensor-sw-temperature",
    #         "--bootstrap-server",
    #         "factory-kafka-cluster-kafka-bootstrap:9092",
    #     ],
    #     shell=True,
    # )

    # sleep(30)
    # log_proc.terminate()
    # logger.info("PASS: Found expected output in kafka log")


def get_log_output(app_string, namespace):
    cmd_out = subprocess.run(
        [oc, "logs", "-l", app_string, "--since=10s", "-n", namespace],
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
