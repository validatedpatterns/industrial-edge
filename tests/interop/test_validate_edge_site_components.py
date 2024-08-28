import logging
import os

import pytest
from ocp_resources.route import Route
from openshift.dynamic.exceptions import NotFoundError
from validatedpatterns_tests.interop import application, components, edge_util

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"

"""
Validate following manuela components pods and endpoints on
edge site (line server):

1) argocd
2) ACM agents
3) manuela-data-lake-factory-mirror-maker
    a) amq stream cluster operator
    b) factory to central mirror maker
4) manuela-stormshift-line-dashboard
    a) line dashboard application
5) manuela-stormshift-machine-sensor
    a) machine sensors app
6) manuela-stormshift-messaging
    a) amq broker operator and amq to MQTT broker
    b) seldon controller
    c) camel-k operator
    d) mqtt2kafka integration
7) applications health (Applications deployed through argocd)
"""


@pytest.mark.test_validate_edge_site_components
def test_validate_edge_site_components():
    logger.info("Checking Openshift version on edge site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")


@pytest.mark.validate_edge_site_reachable
def test_validate_edge_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if edge site API end point is reachable")
    namespace = "openshift-gitops"
    sub_string = "argocd-dex-server-token"
    try:
        edge_api_url = application.get_site_api_url(kube_config)
        edge_api_response = application.get_site_api_response(
            openshift_dyn_client, edge_api_url, namespace, sub_string
        )
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        assert False, e

    if edge_api_response.status_code != 200:
        err_msg = "Edge site is not reachable. Please check the deployment."
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Edge site is reachable")


@pytest.mark.validate_argocd_reachable_edge_site
def test_validate_argocd_reachable_edge_site(openshift_dyn_client):
    logger.info("Check if argocd route/url on edge site is reachable")
    namespace = "openshift-gitops"
    name = "openshift-gitops-server"
    sub_string = "argocd-dex-server-token"
    logger.info("Check if argocd route/url on edge site is reachable")
    try:
        argocd_route_url = application.get_argocd_route_url(
            openshift_dyn_client, namespace, name
        )
        argocd_route_response = application.get_site_api_response(
            openshift_dyn_client, argocd_route_url, namespace, sub_string
        )
    except StopIteration:
        err_msg = "Argocd url/route is missing in open-cluster-management namespace"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    except AssertionError:
        err_msg = "Bearer token is missing for argocd-dex-server"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(f"Argocd route response : {argocd_route_response}")

    if argocd_route_response.status_code != 200:
        err_msg = "Argocd is not reachable. Please check the deployment"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


@pytest.mark.check_pod_status_edge
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")

    err_msg = []
    failed_pods = []
    missing_pods = []
    missing_projects = []
    projects = [
        "openshift-operators",
        "open-cluster-management-agent",
        "open-cluster-management-agent-addon",
        "manuela-stormshift-line-dashboard",
        "manuela-stormshift-machine-sensor",
        "openshift-gitops",
    ]

    missing_projects = components.check_project_absense(openshift_dyn_client, projects)

    for project in projects:
        missing_pods += components.check_pod_absence(openshift_dyn_client, project)
        failed_pods += components.check_pod_status(openshift_dyn_client, project)

    if missing_projects:
        err_msg.append(f"The following namespaces are missing: {missing_projects}")

    if missing_pods:
        err_msg.append(
            f"The following namespaces have no pods deployed: {missing_pods}"
        )

    if failed_pods:
        err_msg.append(f"The following pods are failed: {failed_pods}")

    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pod status check succeeded.")


@pytest.mark.validate_manuela_stormshift_line_dashboard_reachable_edge_site
def test_validate_manuela_stormshift_line_dashboard_reachable_edge_site(
    openshift_dyn_client,
):
    namespace = "manuela-stormshift-line-dashboard"
    logger.info(
        "Check if manuela-stormshift-line-dashboard route/url on edge site is"
        " reachable"
    )

    try:
        for route in Route.get(
            dyn_client=openshift_dyn_client,
            namespace=namespace,
            name="line-dashboard",
        ):
            logger.info(route.instance)
            if "host" in route.instance.spec:
                line_dashboard_route_url = route.instance.spec.host
            else:
                line_dashboard_route_url = route.instance.status.ingress[0].host

    except NotFoundError:
        err_msg = f"Line dashboard url/route is missing in {namespace} namespace"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    final_line_dashboard_route_url = f"{'http://'}{line_dashboard_route_url}"
    logger.info(f"line dashboard route/url : {final_line_dashboard_route_url}")

    bearer_token = edge_util.get_long_live_bearer_token(
        dyn_client=openshift_dyn_client,
        namespace="openshift-gitops",
        sub_string="argocd-dex-server-token",
    )
    if not bearer_token:
        err_msg = "Bearer token is missing for argocd-dex-server"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.debug(f"Bearer token : {bearer_token}")

    line_dashboard_route_response = edge_util.get_site_response(
        site_url=final_line_dashboard_route_url, bearer_token=bearer_token
    )

    logger.info(f"line dashboard route response : {line_dashboard_route_response}")

    if line_dashboard_route_response.status_code != 200:
        err_msg = "Line dashboard is not reachable. Please check the deployment."
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Line dashboard is reachable")


@pytest.mark.validate_argocd_applications_health_edge_site
def test_validate_argocd_applications_health_edge_site(openshift_dyn_client):
    unhealthy_apps = []
    logger.info("Get all applications deployed by argocd on edge site")
    projects = ["openshift-gitops", "industrial-edge-factory"]
    for project in projects:
        unhealthy_apps += application.get_argocd_application_status(
            openshift_dyn_client, project
        )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on edge site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on edge site are healthy.")
