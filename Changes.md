# Changes

## October 24, 2022

* Automatic common/ update #155 - this new update include the
  addition of global.clusterVersion as a new helm variable which represents the OCP
  Major.Minor cluster version. By default now a user can add a
  values-<ocpversion>-<clustergroup>.yaml file to have specific cluster version
  overrides (e.g. values-4.10-hub.yaml). Will need Validated Patterns Operator >= 0.0.6
  when deploying with the operator. Note: When using the ArgoCD Hub and spoke model,
  you cannot have spokes with a different version of OCP than the hub.

## October 25, 2022

* Switch to newer setup-helm version
* Drop helmlint, simplify kubeconform and super-linter
* Add ocpversion values files #157 - This adds the support needed to support different OpenShift versions.
  Subscription channels and CSVs change from time to time especially in different OpenShift versions. The
  values-<ocpversion>-<clusterGroup>.yaml files assist us to be able to deploy the supported subscriptions
  to the OpenShift version we are deploying the Validated Pattern.
* Additions:
  * Added values-4.10-datacenter.yaml
  * Added values-4.11-datacenter.yaml
  * Updated values-datacenter.yaml
* Additional Updates:
  * Added .gitleaks.toml for CI
  * Added proper CI tests
