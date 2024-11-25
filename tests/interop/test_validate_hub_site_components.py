import logging
import os

import pytest
from ocp_resources.storage_class import StorageClass
from validatedpatterns_tests.interop import application, components

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_hub_site_components
def test_validate_hub_site_components(openshift_dyn_client):
    logger.info("Checking Openshift version on hub site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")

    logger.info("Dump PVC and storageclass info")
    pvcs_out = components.dump_pvc()
    logger.info(f"PVCs:\n{pvcs_out}")

    for sc in StorageClass.get(dyn_client=openshift_dyn_client):
        logger.info(sc.instance)


@pytest.mark.validate_hub_site_reachable
def test_validate_hub_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if hub site API end point is reachable")
    err_msg = components.validate_site_reachable(kube_config, openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Hub site is reachable")


@pytest.mark.check_pod_status_hub
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")
    projects = [
        "openshift-operators",
        "open-cluster-management",
        "open-cluster-management-hub",
        "openshift-gitops",
        "industrial-edge-datacenter",
        "manuela-tst-all",
        "openshift-pipelines",
        "manuela-data-lake",
        "vault",
    ]
    err_msg = components.check_pod_status(openshift_dyn_client, projects)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pod status check succeeded.")


# No longer needed for ACM 2.7
#
# @pytest.mark.validate_acm_route_reachable
# def test_validate_acm_route_reachable(openshift_dyn_client):
#     namespace = "open-cluster-management"

#     logger.info("Check if ACM route is reachable")
#     try:
#         for route in Route.get(
#             dyn_client=openshift_dyn_client,
#             namespace=namespace,
#             name="multicloud-console",
#         ):
#             acm_route_url = route.instance.spec.host
#     except NotFoundError:
#         err_msg = (
#             "ACM url/route is missing in open-cluster-management namespace"
#         )
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg

#     final_acm_url = f"{'http://'}{acm_route_url}"
#     logger.info(f"ACM route/url : {final_acm_url}")

#     bearer_token = get_long_live_bearer_token(
#         dyn_client=openshift_dyn_client,
#         namespace=namespace,
#         sub_string="multiclusterhub-operator-token",
#     )
#     if not bearer_token:
#         err_msg = (
#             "Bearer token is missing for ACM in open-cluster-management"
#             " namespace"
#         )
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.debug(f"ACM bearer token : {bearer_token}")

#     acm_route_response = get_site_response(
#         site_url=final_acm_url, bearer_token=bearer_token
#     )

#     logger.info(f"ACM route response : {acm_route_response}")

#     if acm_route_response.status_code != 200:
#         err_msg = "ACM is not reachable. Please check the deployment"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.info("PASS: ACM is reachable.")


@pytest.mark.validate_argocd_reachable_hub_site
def test_validate_argocd_reachable_hub_site(openshift_dyn_client):
    logger.info("Check if argocd route/url on hub site is reachable")
    err_msg = components.validate_argocd_reachable(openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


@pytest.mark.validate_acm_self_registration_managed_clusters
def test_validate_acm_self_registration_managed_clusters(openshift_dyn_client):
    logger.info("Check ACM self registration for edge site")
    kubefiles = [os.getenv("KUBECONFIG_EDGE")]
    err_msg = components.validate_acm_self_registration_managed_clusters(
        openshift_dyn_client, kubefiles
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Edge site is self registered")


# @pytest.mark.skip
# @pytest.mark.validate_jupyterhub_pods_hub_site
# def test_validate_jupyterhub_pods_hub_site(openshift_dyn_client):
#     pods_down = 0
#     namespace = "manuela-ml-workspace"
#     logger.info(
#         "Check if jupyterhub pods are in 'Running' state in" f" {namespace} namespace"
#     )

#     try:
#         jupyterhub_pods = Pod.get(
#             dyn_client=openshift_dyn_client,
#             namespace=namespace,
#             label_selector="deploymentconfig=jupyterhub",
#         )
#         pod = next(jupyterhub_pods)
#     except StopIteration:
#         err_msg = f"There are no jupyterhub pods in {namespace} namespace"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg

#     for pod in jupyterhub_pods:
#         container = pod.instance.status.containerStatuses[0]
#         podname, containername = pod.instance.metadata.name, container.name
#         logger.info(f"{podname}: {containername}: Ready: {container.ready}")

#         # The jupyterhub container for 2 of the 3 jupyterhub pods should
#         # show 'Waiting to become leader' status.
#         # One jupyterhub pod should show all containers ready.
#         if container.ready is not True:
#             log_out = subprocess.run(
#                 [
#                     oc,
#                     "logs",
#                     "-n",
#                     "manuela-ml-workspace",
#                     "-c",
#                     containername,
#                     podname,
#                 ],
#                 capture_output=True,
#             )
#             log_out = log_out.stdout.decode("utf-8")
#             logger.info(f"Log for container '{containername}' in pod '{podname}':")
#             logger.info(log_out)
#             pods_down += 1

#     if int(pods_down) > 2:
#         err_msg = "All jupyterhub pods deployed in manuela-ml-workspace failed"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.info(
#             "PASS: All jupyterhub pods deployed in manuela-ml-workspace"
#             " namespace are up."
#         )


# @pytest.mark.skip
# @pytest.mark.validate_jupyter_route_reachable
# def test_validate_jupyter_route_reachable(openshift_dyn_client):
#     namespace = "manuela-ml-workspace"

#     logger.info("Check if jupyterhub route/url on hub site is reachable")
#     try:
#         for route in Route.get(
#             dyn_client=openshift_dyn_client,
#             namespace=namespace,
#             name="jupyterhub",
#         ):
#             jupyterhub_route_url = route.instance.spec.host
#     except NotFoundError:
#         err_msg = "Jupyterhub url/route is missing in manuela-ml-workspace namespace"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg

#     final_jupyterhub_url = f"{'http://'}{jupyterhub_route_url}"
#     logger.info(f"Jupyterhub route/url : {final_jupyterhub_url}")

#     bearer_token = get_long_live_bearer_token(
#         dyn_client=openshift_dyn_client,
#         namespace=namespace,
#         sub_string="jupyterhub-hub-token",
#     )

#     if not bearer_token:
#         err_msg = (
#             "Bearer token is missing for jupyterhub in manuela-ml-workspace"
#             " namespace"
#         )
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.debug(f"Jupyterhub bearer token : {bearer_token}")

#     jupyterhub_route_response = get_site_response(
#         site_url=final_jupyterhub_url, bearer_token=bearer_token
#     )

#     logger.info(f"Jupyterhub route response : {jupyterhub_route_response}")

#     if jupyterhub_route_response.status_code != 200:
#         err_msg = "Jupyterhub is not reachable. Please check the deployment"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.info("PASS: Jupyterhub is reachable.")


@pytest.mark.validate_argocd_applications_health_hub_site
def test_validate_argocd_applications_health_hub_site(openshift_dyn_client):
    logger.info("Get all applications deployed by argocd on hub site")
    projects = ["openshift-gitops", "industrial-edge-datacenter"]
    unhealthy_apps = application.get_argocd_application_status(
        openshift_dyn_client, projects
    )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on hub site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on hub site are healthy.")
