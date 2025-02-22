import base64
import logging
import os
import re
import subprocess
import time

import kubernetes
import pytest
from ocp_resources.config_map import ConfigMap
from ocp_resources.route import Route
from ocp_resources.secret import Secret
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError
from validatedpatterns_tests.interop.edge_util import modify_file_content

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


# returns (user, pass, route) tuple
def get_gitea_info():
    kubefile = os.getenv("KUBECONFIG_HUB")
    kexp = os.path.expandvars(kubefile)
    ocp_hub = DynamicClient(
        client=kubernetes.config.new_client_from_config(config_file=kexp)
    )
    logger.info("Getting HUB gitea info")
    try:
        gitea_secret_obj = Secret.get(
            dyn_client=ocp_hub, namespace="vp-gitea", name="gitea-admin-secret"
        )
        gitea_secret = next(gitea_secret_obj)
    except NotFoundError:
        err_msg = "The gitea-admin-secret was not found in ns vp-gitea"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    username = base64.b64decode(gitea_secret.instance.data.username).decode("utf-8")
    password = base64.b64decode(gitea_secret.instance.data.password).decode("utf-8")

    try:
        gitea_route_obj = Route.get(
            dyn_client=ocp_hub, namespace="vp-gitea", name="gitea-route"
        )
        gitea_route = next(gitea_route_obj)
    except NotFoundError:
        err_msg = "The gitea-route was not found in ns vp-gitea"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    route = gitea_route.instance.spec.host

    return (username, password, route)


@pytest.mark.toggle_machine_sensor
def test_toggle_machine_sensor(openshift_dyn_client):
    logger.info("Testing machine-sensor config change")
    project = "manuela-stormshift-machine-sensor"
    cm_name = "machine-sensor-1"
    patterns_repo = f"{os.environ['HOME']}/validated_patterns/industrial-edge"

    try:
        cm_obj = ConfigMap.get(
            dyn_client=openshift_dyn_client, name=cm_name, namespace=project
        )
        cm = next(cm_obj)
    except NotFoundError:
        err_msg = f"The configmap {cm} was not found in project {project}"  # pylint: disable=E0601
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(
        "Verify that 'SENSOR_TEMPERATURE_ENABLED' is 'false' in"
        " machine-sensor-1 configmap"
    )
    temp_sensor_status_pre = cm.instance.data.SENSOR_TEMPERATURE_ENABLED

    logger.info(f"SENSOR_TEMPERATURE_ENABLED is {temp_sensor_status_pre}")

    if temp_sensor_status_pre != "false":
        err_msg = (
            "'SENSOR_TEMPERATURE_ENABLED' is not 'false' for machine-sensor-1"
            " configmap"
        )
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info("Set 'SENSOR_TEMPERATURE_ENABLED' to 'true' and commit change")

    if os.getenv("EXTERNAL_TEST") != "true":
        machine_sensor_file = (
            f"{patterns_repo}/charts/factory/manuela-stormshift/"
            "templates/machine-sensor/machine-sensor-1-configmap.yaml"
        )
    else:
        machine_sensor_file = (
            "../../charts/factory/manuela-stormshift/"
            "templates/machine-sensor/machine-sensor-1-configmap.yaml"
        )
    logger.info(f"File Path : {machine_sensor_file}")

    orig_content = 'SENSOR_TEMPERATURE_ENABLED: "false"'
    new_content = 'SENSOR_TEMPERATURE_ENABLED: "true"'

    logger.info("Modify the file content")
    modify_file_content(
        file_name=machine_sensor_file,
        orig_content=orig_content,
        new_content=new_content,
    )
    (gitea_user, gitea_pass, gitea_route) = get_gitea_info()
    gitea_url = (
        f"https://{gitea_user}:{gitea_pass}@{gitea_route}/{gitea_user}/industrial-edge"
    )
    logger.info(
        f"Using the gitea user {gitea_user} on https://{gitea_route}/{gitea_user}/industrial-edge"
    )
    if gitea_pass == "" or gitea_user == "" or gitea_route == "":
        err_msg = "gitea_pass or gitea_user or gitea_route were empty"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info("Merge the change")
    if os.getenv("EXTERNAL_TEST") != "true":
        cur_dir = patterns_repo
    else:
        cur_dir = os.getcwd()

    # We remove the 'gitea-qe' remote in case it already exists
    subprocess.run(
        [
            "git",
            "remote",
            "remove",
            "gitea-qe",
        ],
        cwd=cur_dir,
    )
    res = subprocess.run(
        [
            "git",
            "-c",
            "http.sslVerify=false",
            "remote",
            "add",
            "gitea-qe",
            "-f",
            gitea_url,
        ],
        cwd=cur_dir,
        capture_output=True,
        text=True,
    )

    logger.info(res.stdout)
    logger.info(res.stderr)

    if res.returncode != 0:
        err_msg = f"Could not fetch remote from gitea_url: {gitea_url}"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    pull = subprocess.run(
        ["git", "-c", "http.sslVerify=false", "pull", "gitea-qe", "main"],
        cwd=cur_dir,
        capture_output=True,
        text=True,
    )

    logger.info(pull.stdout)
    logger.info(pull.stderr)

    subprocess.run(["git", "add", machine_sensor_file], cwd=cur_dir)
    subprocess.run(
        ["git", "commit", "-m", "Toggling SENSOR_TEMPERATURE_ENABLED"],
        cwd=cur_dir,
    )

    push = subprocess.run(
        ["git", "-c", "http.sslVerify=false", "push", "gitea-qe"],
        cwd=cur_dir,
        capture_output=True,
        text=True,
    )
    if push.returncode != 0:
        err_msg = f"Could not push to gitea_url: {gitea_url}"
        logger.error(f"FAIL: {err_msg} - {push.stdout} - {push.stderr}")
        assert False, err_msg

    logger.info(push.stdout)
    logger.info(push.stderr)

    logger.info(
        "Verify that 'SENSOR_TEMPERATURE_ENABLED' is 'true' for"
        " machine-sensor-1 configmap"
    )

    timeout = time.time() + 60 * 10
    while time.time() < timeout:
        time.sleep(10)
        cm_obj = ConfigMap.get(
            dyn_client=openshift_dyn_client, name=cm_name, namespace=project
        )
        cm = next(cm_obj)
        temp_sensor_status_post = cm.instance.data.SENSOR_TEMPERATURE_ENABLED

        logger.info(
            "Current value for SENSOR_TEMPERATURE_ENABLED:"
            f" {temp_sensor_status_post}"
        )
        if temp_sensor_status_post != "true":
            continue
        else:
            break

    if temp_sensor_status_post != "true":
        err_msg = (
            "'SENSOR_TEMPERATURE_ENABLED' is not 'true' for machine-sensor-1"
            " configmap"
        )
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(
        "PASS: 'SENSOR_TEMPERATURE_ENABLED' is 'true' for machine-sensor-1" " configmap"
    )

    logger.info("Pause to allow machine-sensor-1 to begin logging")
    time.sleep(30)

    logger.info("Checking machine-sensor-1 logs for temperature data")
    app_string = "app=machine-sensor-1"
    log_out = get_log_output(app_string, namespace="manuela-stormshift-machine-sensor")
    search_terms = ["Current", "Measure", "temperature"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find temperature data in machine-sensor-1 log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found temperature data in machine-sensor-1 log")


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
