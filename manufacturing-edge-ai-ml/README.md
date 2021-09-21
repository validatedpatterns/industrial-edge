# Prerequisites

1. An OpenShift cluster ( Go to https://console.redhat.com/openshift/create )
1. (Optional) A second OpenShift cluster
1. A github account
1. A quay account

The use of this blueprint depends on having at least one running Red Hat
OpenShift cluster. It is desirable to have a cluster for deploying the data
center assets and a seperate cluster(s) for the factory assets.

If you do not have a running Red Hat OpenShift cluster you can start one on a
public or private cloud by using [Red Hat's cloud
service](https://console.redhat.com/openshift/create).

# How to use

1. Fork this repo on GitHub. It is necessary to fork because your fork will be updated as part of the GitOps and DevOps processes.

1. Clone the forked copy

   `git clone git@github.com:your-username/blueprints.git`

1. Create a local copy of the Helm values file that can safely include credentials

  DO NOT COMMIT THIS FILE
  You do not want to push personal credentials to GitHub.
   ```
   cp blueprints/manufacturing-edge-ai-ml/main/values.yaml ~/values-secret.yaml
   vi ~/values-secret.yaml
   ```

1. Preview the changes
   ```
   cd blueprints/manufacturing-edge-ai-ml/main
   helm template manuela . --values ~/values-secret.yaml --debug
   ```
## Datacenter

TIP: It is recommended to have two shells open so that you can switch between datacenter and factory clusters to run commands. 

1. Login to your cluster using oc login or exporting the KUBECONFIG

   `oc login`  
   or 
   
   `export KUBECONFIG=~/my-ocp-env/datacenter`

1. Apply the changes to your cluster

   `helm install manuela . --values ~/values-secret.yaml`
   
1. Check the operators have been installed 

   `UI -> Installed Operators`

1. Obtain the ArgoCD secret

   `oc -n openshift-gitops extract secrets/openshift-gitops-cluster --to=-`

1. Obtain the Cluster ArgoCD location and log in

   `oc get -n openshift-gitops routes/openshift-gitops-server`
   
1. Check all applications are synchronised

## Having a factory (edge) cluster join the datacenter (hub) 

Rather than provide instructions on creating a factory cluster it is assumed
that an OpenShift cluster has already been created. Use the `openshift-install` program provided at [cloud.redhat.com](https://console.redhat.com/openshift/create "Create an OpenShift cluster")

There are a three ways to join the factory to the datacenter.

* Using the ACM user interface
* Using the `cm` tool
* Using the `clusteradm` tool

# Factory setup using the ACM UI

1. From the datacenter openshift console select ACM from the top right

![](https://github.com/hybrid-cloud-patterns/docs/images/launch-acm-console.png "Launch ACM console")

2. Select the "Import cluster" option beside the highleded Create Cluster button.

![](https://github.com/hybrid-cloud-patterns/docs/images/import-cluster.png "Select Import cluster")

3. On the "Import an existing cluster" page, enter the cluster name and choose Kubeconfig as the "import mode". After pressiming import you will be asked to copy a command that will be used on the factory cluster.

![](https://github.com/hybrid-cloud-patterns/docs/images/import-with-kubeconfig.png "Import using kubeconfig")

Skip to the section [Factory is joined](#factory-is-joined)

## Factory setup using `cm` tool

1. Install the `cm` (cluster management) CLI tool. See details [here](https://github.com/open-cluster-management/cm-cli/#installation)

1. Obtain the KUBECONFIG file from the edge/factory cluster.

1. On the command line login into the hub/datacenter cluster (use `oc login` or export the KUBECONFIG).

1. Run the following command:
```
cm attach cluster --cluster <cluster-name> --cluster-kubeconfig <path-to-KUBECONFIG>
``` 

Skip to the section [Factory is joined](#factory-is-joined)

## Factory setup using `clusteradm` tool

You can also use `clusteradm` to join a cluster. The folloing instructions explain what needs to be done. `clusteradm` is still in testing.

1. To deploy a edge cluster you will need to get the datacenter (or hub) cluster's token. You will need to install `clusteradm`.  On the existing *datacenter cluster*:

   `clusteradm get token`

1. When you run the `clusteradm` command above it replies with the token and also shows you the command to use on the factory. So first you must login to the factory cluster

   `oc login`
   or
   
   `export KUBECONFIG=~/my-ocp-env/factory`

1. Then request to that the factory join the datacenter hub

   `clusteradm join --hub-token <token from clusteradm get token command > <factory cluster name>`

1. Back on the hub cluster accept the join reguest 

   `clusteradm accept --clusters <factory-cluster-name>`

Skip to the next section, [Factory is joined](#factory-is-joined)

## Factory is joined
That's it! Go to your factory (edge) OpenShift console and check for the open-cluster-management-agent pod being launched. Be patient, it will take a while for the ACm agent and agent-addons to launch. After that, the operator OpenShifdt GitOps will run. When it's finished coming up launch the OpenShift GitOps (ArgoCD) console from the top right of the OpenShift console. 

# Structure

https://docs.google.com/presentation/d/e/2PACX-1vSfbN_TbjfYnw-B6hHs-uUQ-8rRzUX27AW4eSxT7dVmBERiBgHS_FWWkgyg5fTsEWL2hj6RYyJqYi7_/pub?start=false&loop=false&delayms=3000

# Uninstalling

1. Turn off auto-sync

   `helm upgrade manuela . --values ~/values-secret.yaml --set gitops.syncPolicy=Manual`

1. Remove the ArgoCD applications (except for manuela-datacenter)

   a. Browse to ArgoCD
   a. Go to Applications
   a. Click delete
   a. Type the application name to confirm
   a. Chose "Foreground" as the propagation policy
   a. Repeat

1. Wait until the deletions succeed

   `manuela-datacenter` should be the only remaining application

1. Complete the uninstall

   `helm delete manuela`

1. Check all namespaces and operators have been removed

# Diagrams

The following diagrams show the different components deployed on the datacenter and the factory.

## Logical

![Logical](diagrams/manufacturing-logical.png)

## Schematic with Networks

![Schema - Networks](diagrams/manufacturing-schema-netw.png)

## Schematic with Dataflows

![Schema - Dataflow](diagrams/manufacturing-schema-df.png)

## Editing the diagrams.

To edit the diagrams in Draw.io you can load them [here](https://redhatdemocentral.gitlab.io/portfolio-architecture-tooling/index.html?#/portfolio-architecture-examples/projects/Mfg-AI-ML-0928.drawio) and save a local copy
