# blueprint-management-hub

This repository contains the _blueprint definitiion_ for a management hub cluster. The purpose of this cluster running on a public cloud or on a central datacenter on prem is to host services such as RHACM (Red Hat Advanced Cluster Manager), Tekton, ArgoCD, etc. and run CI/CD pipelines to test new images, train AI/ML models or gather data from remote edge computing clusters.

It is very important to highlight that this is _just_ one implementation of the *blueprint* concept and it is based on the [Akraino KNI project](https://wiki.akraino.org/display/AK/Kubernetes-Native+Infrastructure+%28KNI%29+Blueprint+Family). This repository describes a blueprint as a set of four different directories:

- 00_install-config
- 01_cluster-mods
- 02_cluster-addons
- 03_services

### 00_install-config

This folder will contain the basic settings for the site, including the base blueprint/profile, and the site name/domain. The following files are needed:

+ **kustomization.yaml**: key file, where it will contain a link to the used blueprint/profile, and a reference to the used patches to customize the site bases:

```yaml
bases:
- git::https://github.com/redhat-edge-computing/blueprint-management-hub.git//profiles/production.gcp/00_install-config

patches:
- install-config.patch.yaml

patchesJson6902:
- target:
    version: v1
    kind: InstallConfig
    name: cluster
  path: install-config.name.patch.yaml

transformers:
- site-config.yaml
```

The entry in bases needs to reference the blueprint being used, and the profile install-config file (in this case `profiles/production.gcp/00_install-config`). The other entries need to be just written literally.

+ **install-config.patch.yaml**: is a patch to modify the domain from the base blueprint. You need to customize with the domain you want to give to your site.
+ **install-config.name.patch.yaml**: is a patch to modify the site name from the base blueprint. You need to customize with the name you want to give to your site.
+ **site-config.yaml**: site configuration file, you can add entries in config to override behaviour of knictl (currently just releaseImageOverride is supported)

### 01_cluster_mods

This is the directory that will contain all the customizations for the basic cluster deployment. You could create patches for modifying number of masters/workers, network settings... everything that needs to be modified on cluster deployment time. It needs to have a basic kustomization.yaml file, that will reference the same level file for the blueprint. This should reflect in a set of manifests located in the same folders that the `openshift-install` binary defines when creates the final manifests.

### 02_cluster_addons and 03_services

Follow same structure as `01_cluster_mods`, but in this case is for adding additional workloads after cluster deployment. They also need to have a `kustomization.yaml` file that references the file of the same level for the blueprint, and can include additional resources and patches. To give a hint of the difference between these two folders, cluster addons could be operators as part of the infra (SRIOV network operator, etc), while services are more application workloads.

As a summary, `00_install-config` and `01_cluster-mods` represent features at deployment time (Day 1) while `02_cluster-addons` and `03_services` are features and applications to deploy once the cluster is up and running (Day 2).

This very same structure will be maintained in all of our blueprint types. There are three types of blueprints:

+ **Base:** the base blueprint contains all the common features your set of OpenShift clusters will require.
+ **Profile:** the profile blueprints will specify configuration related to the footprint where the cluster is going to be deployed on. This repo contains profiles for AWS, GCP and bare metal.
+ **Site:** a site is the definition of just one OpenShift cluster. A site inherits the characteristics of a profile and the base blueprints.

This repository contains a base blueprint, various profiles and only one site definition: 3 masters - 3 workers cluster running on GCP.

## knictl

As part of the Akraino KNI project, a helper tool was developed in order to be able to render these blueprints into something the `openshift-install` binary can accept as input. It is based in [`kustomize`](https://kustomize.io/), a well adopted tool part of the Kubernetes ecosystem. The user can leverage all the potential of `kustomize` in order to create overlays, generate new objects and make very complex blueprints. `knictl` will use the requirements.yaml file located in the profile blueprint to download required binaries, and then render the manifests.

`knictl` tool is not available as a binary, so the user will have to compile it following the next easy steps. The user can either compile locally in its laptop,
or build a container image to use with podman or docker.

### Compile knictl

We assume that the Golang runtime is already installed in your own machine (Linux):

```bash
cd $GOPATH/src
mkdir -p gerrit.akraino.org/kni/
cd gerrit.akraino.org/kni/
git clone "https://gerrit.akraino.org/r/kni/installer"
cd installer
make build
```

You will see the binary `knictl` on that very same folder. It is mandatory to keep `knictl` within that path for the moment since we are using ad-hoc `kustomize` plugins made for this project. As recommendation, yo can create an alias to point to the binary.

Create a `$HOME/.kni` folder and copy the following files:

+ **id_rsa.pub** → needs to contain the public key that you want to use to access your nodes
+ **pull-secret.json** → needs to contain the pull secret previously copied

### Build knictl container

To build the container image, execute the following command inside this repo.

```bash
cd blueprint-management-hub/
podman build -t localhost/knictl:latest -f Containerfile.knictl
```

To easily use knictl container, the user can use this sample alias. 
For an easier troubleshooting, create the folder `~/.kni/tmp/`. We will mount it `/tmp/` inside the container as knictl will write the kustomized renedered manifests there.

```bash
mkdir ~/.kni/tmp/
```

Note this is prepared to mount the AWS credentials folder  `~/.aws`. In case you are using any other provider, modify this alias accordingly.

```bash
alias knictl='podman run -i --rm -v ~/.kni:/root/.kni:Z -v ~/.aws:/root/.aws:ro,z -v ~/.kni/tmp:/tmp:Z localhost/knictl:latest'
```

Finally, create a `$HOME/.kni` folder and copy the following files:

+ **id_rsa.pub** → needs to contain the public key that you want to use to access your nodes
+ **pull-secret.json** → needs to contain the pull secret previously copied



You can find the steps to deploy the following defined sites here:


- [Management Hub cluster running on GCP](sites/edge-mgmt-hub.gcp.devcluster.openshift.com/README.md)
