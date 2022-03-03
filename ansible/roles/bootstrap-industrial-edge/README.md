# Ansible Role: bootstrap-industrial-edge

This role contains all the imperative tasks that are needed to deploy
the Industrial Edge validated pattern onto an OpenShift cluster.

## Requirements
------------

* Pre-deployed Openshift or Kubernetes Cluster
* Must be Cluster Admin to successfully execute this role.
* There are a few tools that you will need to run this role which are listed below.  

| Tool | Description | Download link |
| ----------- | ----------- | ----------- |
| kubernetes.core | The collection includes a variety of Ansible content to help automate the management of applications in Kubernetes and OpenShift clusters, as well as the provisioning and maintenance of clusters themselves | **ansible-galaxy collection install kubernetes.core** |
| Kubernetes Python Cli | The kubernetes.core collection requires the Kubernetes Python client to interact with Kubernetes' APIs. | **pip3 install kubernetes** |
| Python 3 | Python2 is deprecated from 1st January 2020. Please switch to Python3. | RHEL: <br> **yum -y install rh-python36** |


## Role Variables
------------

Most of the variables will be dynamically set for you in this role. Variables that we will be looking for are:

| Variable | Description | Default Value |
| --------- | ---------- | ---------- |
| pattern_repo_dir:  | Pattern directory.  We assume that you start the execution of the ansile role in the pattern working cloned directory. |  "{{ lookup('env', 'PWD') }}" |
| argo_target_namespace: | Target namespace for ArgoCD |manuela-ci |
| pattern: | Name of the validated pattern | industrial-edge |
| component: | Name of the component to deploy |datacenter |
| secret_name: | Name of the ArgoCD secret in OpenShift | "argocd-env" |
| values_secret: | Location of the values-secret.yaml file | "{{ lookup('env', 'HOME') }}/values-secret.yaml" |
| values_global: | Location of the values-global.yaml file | "{{ pattern_repo_dir }}/values-secret.yaml" |
| kubeconfig: | Environment variable for KUBECONFIG | "{{ lookup('env', 'KUBECONFIG') }}"|
| vault_init_file: | Init Vault file which will contain Vault tokens etc | "{{ pattern_repo_dir }}/common/pattern-vault.init"|
| vault_ns: | Namespace for Vault | "vault"|                                     
| vault_pod: | Name of the initial Vault pod | "vault-0"|           
| vault_path: | Path to the Vault secrets for the Hub | "secret/hub"|
| debug: | Whether or not to display debug info | False |

> NOTE: The role is designed to use the current *git* branch that you are working on. It is also designed to derive the variables values using your environment. 


## Dependencies
------------

None

## Site.yaml Playbook
------------

The initial playbook can be found under ansible/site.yaml and will execute the bootstrap role.

```yaml
- name: Industrial Edge bootstrap 
  hosts: localhost
  connection: local
  roles:
    - bootstrap-industrial-edge
```

To start the execution of the role execute the following:

```sh
$ pwd
/home/claudiol/work/blueprints-space/industrial-edge
$ ansible-playbook ansible/site.yaml 
```

License
-------

BSD

Author Information
------------------
Lester Claudio (claudiol@redhat.com) <br>
Jonathan Rickard (jrickard@redhat.com)<br>
Michele Baldessari (mbaldess@redhat.com)<br>
Martin Jackson (mhjacks@redhat.com)