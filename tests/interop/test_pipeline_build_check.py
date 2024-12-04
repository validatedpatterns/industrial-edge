import logging
import os
import re
import subprocess
import time

import kubernetes
import pytest
from ocp_resources.pod import Pod
from openshift.dynamic import DynamicClient

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.pipeline_build_check
def test_pipeline_build_check(openshift_dyn_client):
    logger.info("Running pipeline build check")
    regex = "[0-9]{1,4}$"
    project_hub = "manuela-tst-all"
    project_edge = "manuela-stormshift-messaging"
    kubefile = os.getenv("KUBECONFIG_EDGE")
    kubefile_exp = os.path.expandvars(kubefile)
    openshift_dyn_client_edge = DynamicClient(
        client=kubernetes.config.new_client_from_config(config_file=kubefile_exp)
    )

    logger.info("Get pod list for manuela-tst-all on hub site")
    try:
        pods = Pod.get(
            dyn_client=openshift_dyn_client,
            namespace=project_hub,
            label_selector="app=messaging",
        )
        pod = next(pods)
    except StopIteration:
        err_msg = f"No pods were found in project {project_hub}"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    starting_image_hub = pod.instance.spec.containers[0].image
    starting_build_hub = re.search(regex, starting_image_hub)

    try:
        pods = Pod.get(
            dyn_client=openshift_dyn_client_edge,
            namespace=project_edge,
            label_selector="app=messaging",
        )
        pod = next(pods)
    except StopIteration:
        err_msg = f"No pods were found in project {project_edge}"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    starting_image_edge = pod.instance.spec.containers[0].image
    starting_build_edge = re.search(regex, starting_image_edge)

    logger.info("Apply build-test-and-run chart")
    if os.getenv("EXTERNAL_TEST") != "true":
        chart = (
            f"{os.environ['HOME']}"
            + "/validated_patterns/industrial-edge/charts/"
            + "datacenter/pipelines/extra/build-and-test-iot-consumer.yaml"
        )
    else:
        chart = (
            "../../charts/datacenter/pipelines/extra/build-and-test-iot-consumer.yaml"
        )

    logger.info(f"Chart: {chart}")

    apply_chart = subprocess.run(
        [
            oc,
            "create",
            "-f",
            chart,
        ],
        capture_output=True,
        text=True,
    )
    logger.info(apply_chart.stdout)
    logger.info(apply_chart.stderr)

    if apply_chart.stderr:
        err_msg = "Failed to apply chart"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    timeout = time.time() + 60 * 30
    while time.time() < timeout:
        time.sleep(60)

        pods = Pod.get(
            dyn_client=openshift_dyn_client,
            namespace=project_hub,
            label_selector="app=messaging",
        )
        pod = next(pods)

        current_image_hub = pod.instance.spec.containers[0].image
        current_build_hub = re.search(regex, current_image_hub)

        logger.info(f"Checking image (hub): {current_image_hub}")

        if int(current_build_hub.group()) > int(starting_build_hub.group()):
            break

    if int(current_build_hub.group()) <= int(starting_build_hub.group()):
        logger.info("Checking pod status in manuela-ci namespace")
        pods = Pod.get(dyn_client=openshift_dyn_client, namespace="manuela-ci")

        for pod in pods:
            logger.info(
                f"Checking pod: {pod.instance.metadata.name}: {pod.instance.status.phase}"
            )
            if pod.instance.status.phase == "Failed":
                logger.info(
                    f"WARNING: Pod {pod.instance.metadata.name} in the"
                    " manuela-ci namespace has failed"
                )
                log_out = subprocess.run(
                    [
                        oc,
                        "logs",
                        "--all-containers=true",
                        "-n",
                        "manuela-ci",
                        pod.instance.metadata.name,
                    ],
                    capture_output=True,
                )
                log_out = log_out.stdout.decode("utf-8")
                logger.info(log_out)
        err_msg = (
            "Build number on hub site has not been incremented. Check for"
            " pipeline failures in above output."
        )
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("Build number has incremented on hub site")

    pods = Pod.get(
        dyn_client=openshift_dyn_client_edge,
        namespace=project_edge,
        label_selector="app=messaging",
    )
    pod = next(pods)

    current_image_edge = pod.instance.spec.containers[0].image
    current_build_edge = re.search(regex, current_image_edge)
    logger.info(f"Checking image (edge): {current_image_edge}")

    if int(current_build_edge.group()) != int(starting_build_edge.group()):
        err_msg = "Build number has changed on edge site"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("Build number is unchanged on edge site")
        logger.info("PASS: Pipeline build check succeeded")
