## How to deploy the management hub cluster on GCP

First of all you need to have your Google Cloud Platform service account file located in the following path:

`$HOME/.gcp/osServiceAccount.json`

The OpenShift installer binary will read that file if gcp is set as a platform. From the path where the `knictl` binary is located, and in order to pull our edge-mgmt-hub site and its requirements, please execute:

`knictl fetch_requirements github.com/redhat-edge-computing/blueprint-management-hub/sites/mgmt-edge-hub.gcp.devcluster.openshift.com/`

This command will download the site blueprint definition, and all its requirements (oc, openshift-install, kustomize, etc) to the `$HOME/.kni/`. Every site will have a separate directory within that location. The next step involves the actual rendering of the manifests (site + profile + base) into one set of manifests via kustomize that we can pass to the openshift-install binary.

`knictl prepare_manifests edge-mgmt-hub.gcp.devcluster.openshift.com`

If everything goes well, the command will get out some instructions to deploy the cluster. It's basically asking you to run `openshift-install` binary pointing to where the final manifests created by `knictl` are:

`$HOME/.kni/edge-mgmt-hub.gcp.devcluster.openshift.com/requirements/openshift-install create cluster --dir=$HOME/.kni/edge-mgmt-hub.gcp.devcluster.openshift.com/final_manifests --log-level debug`

Wait until the deployment is completed, and you will information about console endpoint, kubeadmin password and kubeconfig path.

If you have manifests that you want to deploy as Day 2 operations located in any of the 02_cluster-addons or 03_services directories, you can deploy them running the following command:

`knictl apply_workloads edge-mgmt-hub.gcp.devcluster.openshift.com`

This is basically running kustomize to build and render all the manifests enabling alpha plugins, and apply them via oc/kubectl.
