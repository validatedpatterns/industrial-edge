import logging
import os
import re
import subprocess
import time

import pytest
from ocp_resources.pipeline import Pipeline
from ocp_resources.pipelineruns import PipelineRun
from ocp_resources.task_run import TaskRun

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_pipelineruns
def test_validate_pipelineruns(openshift_dyn_client):
    project = "manuela-ci"

    expected_pipelines = [
        "seed",
        "build-base-images",
        "seed-iot-anomaly-detection",
        "seed-iot-consumer",
        "seed-iot-frontend",
        "seed-iot-software-sensor",
    ]

    expected_pipelineruns = [
        "seed-run",
        "build-base-images-run",
        "seed-iot-anomaly-detection-run",
        "seed-iot-consumer-run",
        "seed-iot-frontend-run",
        "seed-iot-software-sensor-run",
    ]

    found_pipelines = []
    found_pipelineruns = []
    passed_pipelineruns = []
    failed_pipelineruns = []

    logger.info("Checking Openshift pipelines")

    # FAIL here if no pipelines are found
    try:
        pipelines = Pipeline.get(dyn_client=openshift_dyn_client, namespace=project)
        next(pipelines)
    except StopIteration:
        err_msg = "No pipelines were found"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    for pipeline in Pipeline.get(dyn_client=openshift_dyn_client, namespace=project):
        for expected_pipeline in expected_pipelines:
            match = expected_pipeline + "$"
            if re.match(match, pipeline.instance.metadata.name):
                if pipeline.instance.metadata.name not in found_pipelines:
                    logger.info(f"found pipeline: {pipeline.instance.metadata.name}")
                    found_pipelines.append(pipeline.instance.metadata.name)
                    break

    if len(expected_pipelines) == len(found_pipelines):
        logger.info("Found all expected pipelines")
    else:
        err_msg = "Some or all pipelines are missing"
        logger.error(
            f"FAIL: {err_msg}:\nExpected: {expected_pipelines}\nFound: {found_pipelines}"
        )
        assert False, err_msg

    logger.info("Checking Openshift pipeline runs")
    timeout = time.time() + 3600

    # FAIL here if no pipelineruns are found
    try:
        pipelineruns = PipelineRun.get(
            dyn_client=openshift_dyn_client, namespace=project
        )
        next(pipelineruns)
    except StopIteration:
        err_msg = "No pipeline runs were found"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    while time.time() < timeout:
        for pipelinerun in PipelineRun.get(
            dyn_client=openshift_dyn_client, namespace=project
        ):
            for expected_pipelinerun in expected_pipelineruns:
                if re.search(expected_pipelinerun, pipelinerun.instance.metadata.name):
                    if pipelinerun.instance.metadata.name not in found_pipelineruns:
                        logger.info(
                            f"found pipelinerun: {pipelinerun.instance.metadata.name}"
                        )
                        found_pipelineruns.append(pipelinerun.instance.metadata.name)
                        break

        if len(expected_pipelineruns) == len(found_pipelineruns):
            break
        else:
            time.sleep(60)
            continue

    if len(expected_pipelineruns) == len(found_pipelineruns):
        logger.info("Found all expected pipeline runs")
    else:
        err_msg = "Some pipeline runs are missing"
        logger.error(
            f"FAIL: {err_msg}:\nExpected: {expected_pipelineruns}\nFound: {found_pipelineruns}"
        )
        assert False, err_msg

    logger.info("Checking Openshift pipeline run status")
    timeout = time.time() + 3600

    while time.time() < timeout:
        for pipelinerun in PipelineRun.get(
            dyn_client=openshift_dyn_client, namespace=project
        ):
            if pipelinerun.instance.status.conditions[0].reason == "Succeeded":
                if pipelinerun.instance.metadata.name not in passed_pipelineruns:
                    logger.info(
                        f"Pipeline run succeeded: {pipelinerun.instance.metadata.name}"
                    )
                    passed_pipelineruns.append(pipelinerun.instance.metadata.name)
            elif pipelinerun.instance.status.conditions[0].reason == "Running":
                logger.info(
                    f"Pipeline {pipelinerun.instance.metadata.name} is still running"
                )
            else:
                reason = pipelinerun.instance.status.conditions[0].reason
                logger.info(
                    f"Pipeline run FAILED: {pipelinerun.instance.metadata.name} Reason: {reason}"
                )
                if pipelinerun.instance.metadata.name not in failed_pipelineruns:
                    failed_pipelineruns.append(pipelinerun.instance.metadata.name)

        logger.info(f"Failed pipelineruns: {failed_pipelineruns}")
        logger.info(f"Passed pipelineruns: {passed_pipelineruns}")

        if (len(failed_pipelineruns) + len(passed_pipelineruns)) == len(
            expected_pipelines
        ):
            break
        else:
            time.sleep(60)
            continue

    if ((len(failed_pipelineruns)) > 0) or (
        len(passed_pipelineruns) < len(expected_pipelineruns)
    ):
        logger.info("Checking Openshift task runs")

        # FAIL here if no task runs are found
        try:
            taskruns = TaskRun.get(dyn_client=openshift_dyn_client, namespace=project)
            next(taskruns)
        except StopIteration:
            err_msg = "No task runs were found"
            logger.error(f"FAIL: {err_msg}")
            assert False, err_msg

        for taskrun in TaskRun.get(dyn_client=openshift_dyn_client, namespace=project):
            if taskrun.instance.status.conditions[0].status == "False":
                reason = taskrun.instance.status.conditions[0].reason
                logger.info(
                    f"Task FAILED: {taskrun.instance.metadata.name} Reason: {reason}"
                )

                message = taskrun.instance.status.conditions[0].message
                logger.info(f"message: {message}")

                try:
                    cmdstring = re.search("for logs run: kubectl(.*)$", message).group(
                        1
                    )
                    cmd = str(oc + cmdstring)
                    logger.info(f"CMD: {cmd}")
                    cmd_out = subprocess.run(cmd, shell=True, capture_output=True)

                    logger.info(cmd_out.stdout.decode("utf-8"))
                    logger.info(cmd_out.stderr.decode("utf-8"))
                except AttributeError:
                    logger.error("No logs to collect")

        err_msg = "Some or all tasks have failed"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    else:
        logger.info("PASS: Pipeline verification succeeded.")
