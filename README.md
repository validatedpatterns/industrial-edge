# Start Here

If you've followed a link to this repo, but are not really sure what it contains
or how to use it, head over to http://hybrid-cloud-patterns.io/industrial-edge/
for additional context before continuing.

# Prerequisites

1. An OpenShift cluster ( Go to https://console.redhat.com/openshift/create )
1. (Optional) A second OpenShift cluster
1. A github account (and a token for it with repos permissions, to read from and write to your forks)
1. A quay account with the following repos set as public:
- http-ionic
- httpd-ionic
- iot-anomaly-detection
- iot-consumer
- iot-frontend
- iot-software-sensor
5. The helm binary, see https://helm.sh/docs/intro/install/

The use of this blueprint depends on having at least one running Red Hat
OpenShift cluster. It is desirable to have a cluster for deploying the data
center assets and a seperate cluster(s) for the factory assets.

If you do not have a running Red Hat OpenShift cluster you can start one on a
public or private cloud by using [Red Hat's cloud
service](https://console.redhat.com/openshift/create).

# How to deploy

1. Fork the [manuela-dev](https://github.com/hybrid-cloud-patterns/manuela-dev) repo on GitHub.  It is necessary to fork this repo because the GitOps framework will push tags to this repo that match the versions of software that it will deploy.
1. Fork this repo on GitHub. It is necessary to fork because your fork will be updated as part of the GitOps and DevOps processes.

1. Clone the forked copy of this repo.

   ```
   git clone --recurse-submodules git@github.com:your-username/industrial-edge.git
   ```

1. Create a local copy of the Helm values file that can safely include credentials

  DO NOT COMMIT THIS FILE

  You do not want to push personal credentials to GitHub.
   ```
   cp values-secret.yaml.template ~/values-secret.yaml
   vi ~/values-secret.yaml
   ```

1. Customize the deployment for your cluster

   ```
   vi values-global.yaml
   git add values-global.yaml
   git commit values-global.yaml
   git push
   ```

1. Preview the changes
   ```
   make show
   ```

1. Login to your cluster using oc login or exporting the KUBECONFIG

   ```
   oc login
   ```

   or

   ```
   export KUBECONFIG=~/my-ocp-env/datacenter/kubeconfig
   ```

1. Apply the changes to your cluster

   ```
   make install
   ```

1. Check the operators have been installed

   ```
   OpenShift UI -> Installed Operators
   ```
   It takes time for all the operators and other components to be installed. It is useful to go back and forth between the OpenShift GitOps UI (see the following two steps) and the OpenShift UI to watch as applications and oeprators come up.  

1. Obtain the ArgoCD urls and passwords

   The URLs and login credentials for ArgoCD change depending on the pattern
   name and the site names they control.  Follow the instructions below to find
   them, however you choose to deploy the pattern.

   Display the fully qualified domain names, and matching login credentials, for
   all ArgoCD instances:

   ```
   ARGO_CMD=`oc get secrets -A -o jsonpath='{range .items[*]}{"oc get -n "}{.metadata.namespace}{" routes; oc -n "}{.metadata.namespace}{" extract secrets/"}{.metadata.name}{" --to=-\\n"}{end}' | grep gitops-cluster`
   eval $ARGO_CMD
   ```

   The result should look something like:

   ```
   NAME                       HOST/PORT                                                                                         PATH      SERVICES                   PORT    TERMINATION            WILDCARD
   datacenter-gitops-server   datacenter-gitops-server-industrial-edge-datacenter.apps.mycluster.mydomain.com          datacenter-gitops-server   https   passthrough/Redirect   None
   # admin.password
   2F6kgITU3DsparWyC

   NAME                    HOST/PORT                                                                                   PATH   SERVICES                PORT    TERMINATION            WILDCARD
   factory-gitops-server   factory-gitops-server-industrial-edge-factory.apps.mycluster.mydomain.com          factory-gitops-server   https   passthrough/Redirect   None
   # admin.password
   K4ctDIm3fH7ldhs8p

   NAME                      HOST/PORT                                                                              PATH   SERVICES                  PORT    TERMINATION            WILDCARD
   cluster                   cluster-openshift-gitops.apps.mycluster.mydomain.com                          cluster                   8080    reencrypt/Allow        None
   kam                       kam-openshift-gitops.apps.mycluster.mydomain.com                              kam                       8443    passthrough/None       None
   openshift-gitops-server   openshift-gitops-server-openshift-gitops.apps.mycluster.mydomain.com          openshift-gitops-server   https   passthrough/Redirect   None
   # admin.password
   WNklRCD8EFg2zK034
   ```


1. Check all applications are synchronized

# Factory (Edge) setup

It's time to connect a "remote" factory cluster to the data center (hub).

## Factory setup using the ACM UI

1. Locate the kubeconfig for your factory (edge) cluster 

1. Import the kubeconfig into hub (data center) cluster

   Select the `Import Cluster` option beside the highlighted Create Cluster button.

   On the "Import an existing cluster" page, enter the cluster name and choose Kubeconfig as the "import mode". Copy the kubeconfig details into the space provided. 

   Note: After pressing `Import` you will be prompted to copy a command that can be used on the factory cluster. INGORE this message. It will go away, and is only useful if something goes wrong and you need to manually import. 

## Factory setup using `cm` tool

1. If you don't already have the `cm` tool then build from [here](https://github.com/open-cluster-management/cm-cli)

1. Locate the factory's kubeconfig path.

1. While logged into the data center (hub) run the following command on the hub:
   ```
   cm attach cluster --cluster <cluster-name> --cluster-kubeconfig <path-of-kubeconfig>
   ```
 
## Factory setup using `clusteradm` tool

You can also use `clusteradm` to join a cluster. The following instructions explain what needs to be done. clusteradm is still in testing. It's useful to have two shells available for these steps. One logged into factory (edge) and one logged into data center (hub). Move over and back based on the location of the command needs below.

1. If you don't already have the `clusteradm` tool then download from [here](https://github.com/open-cluster-management-io/clusteradm/releases)

1. Get the a token from the data center (hub) cluster using this the following command on the data center (hub) cluster:

   ```
    clusteradm get token
   ``` 

   This will return a token that you can copy.
      
1. On the factory request to join to the data center (hub) 

   ```
   clusteradm join --hub-token <paste-token>
   ```

1. Back on the hub cluster UI accept the join request.
 
## The factory has joined

You are done! Now be patient because it takes some time for everything to happen on the factory. What will happen is:

1. The hub will push down an ACM agent to the factory (edge).

1. Once the agent is installed it will install OpenShift GitOps.

1. OpenShift GitOps takes over and installs everything else. 
 
You can check your Installed Operators on your factory (edge) OpenShift cluster and wait to see the OpenShift GitOps operator install. If you're really impatient, you can also check Workloads for the  `open-cluster-management-agent`  project to appear. This happens before OpenShift GitOps is installed.  

When OpenShift GitOps installed and ready, launch the OpenShift GitOps (ArgoCD) console from up at the top right of the OpenShift console.
# Pattern Layout and Structure

https://slides.com/beekhof/hybrid-cloud-patterns

# Uninstalling

**Probably wont work**

1. Turn off auto-sync

   `helm upgrade manuela . --values ~/values-secret.yaml --set global.options.syncPolicy=Manual`

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

![Logical](docs/images/manufacturing-logical.png)

## Schematic with Networks

![Schema - Networks](docs/images/manufacturing-schema-netw.png)

## Schematic with Dataflows

![Schema - Dataflow](docs/images/manufacturing-schema-df.png)

## Editing the diagrams.

To edit the diagrams in Draw.io you can load them [here](https://redhatdemocentral.gitlab.io/portfolio-architecture-tooling/index.html?#/portfolio-architecture-examples/projects/Mfg-AI-ML-0928.drawio) and save a local copy
