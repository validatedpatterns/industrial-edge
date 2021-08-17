# How to use

1. Fork this repo on GitHub 
1. Clone the forked copy
   `git clone git@github.com:your-username/blueprints.git`

1. Create a local copy of the Helm values file that can safely include credentials

  DO NOT COMMIT THIS FILE
   ```
   cp blueprints/manufacturing-edge-ai-ml/main/values.yaml ~/values-secret.yaml
   vi ~/values-secret.yaml
   ```

1. Preview the changes
   ```
   cd blueprints/manufacturing-edge-ai-ml/main
   helm template manuela . --values ~/values-secret.yaml --debug
   ```
1. Apply it to your cluster
   ```
   oc login
   helm install manuela . --values ~/values-secret.yaml
   ```
1. Check the operators have been installed

   `UI -> Installed Operators`

1. Obtain the ArgoCD secret

   `oc -n openshift-gitops extract secrets/openshift-gitops-cluster --to=-`

1. Obtain the Cluster ArgoCD location and log in

   `oc get -n openshift-gitops routes/openshift-gitops-server`
   
1. Check all applications are synchronised

1. Obtain the Manuela ArgoCD secret

   `oc -n manuela-ci extract secrets/manuela-argocd-cluster --to=-`

1. Obtain the Manuela ArgoCD location and log in

   `oc get -n manuela-ci routes/manuela-argocd-server`

1. Check all applications are synchronised

# Structure

https://docs.google.com/presentation/d/e/2PACX-1vSfbN_TbjfYnw-B6hHs-uUQ-8rRzUX27AW4eSxT7dVmBERiBgHS_FWWkgyg5fTsEWL2hj6RYyJqYi7_/pub?start=false&loop=false&delayms=3000