# How to use

1. Fork this repo on GitHub 
1. Clone the forked copy
   `git clone git@github.com:your-username/blueprints.git`
1. Create a local copy of the Helm values file that includes credentials

  DO NOT COMMIT THIS FILE
   ```
   cp blueprints/manufacturing-edge-ai-ml/values.yaml blueprints/manufacturing-edge-ai-ml/values-secret.yaml
   vi blueprints/manufacturing-edge-ai-ml/values-secret.yaml
   ```

1. Preview the changes
   ```
   cd blueprints/manufacturing-edge-ai-ml
   helm template manuela . --values values-secret.yaml --debug
   ```
1. Apply it to your cluster
   ```
   oc login
   helm install manuela . --values values-secret.yaml
   ```
1. Check the operators have been installed

   `UI -> Installed Operators`

1. Obtain the ArgoCD secret

   `oc get -n openshift-gitops secrets/openshift-gitops-cluster -o json | jq '.data' | grep admin.password | awk -F: '{print $2}' | tr -d \"\  | base64 -d`

1. Obtain the Cluster ArgoCD location and log in

   `oc get -n openshift-gitops routes/openshift-gitops-server`
   
1. Check all applications are synchronised

1. Obtain the Manuela ArgoCD secret

   `oc get -n manuela-ci secrets/manuela-argocd-cluster -o json | jq '.data' | grep admin.password | awk -F: '{print $2}' | tr -d \"\  | base64 -d`

1. Obtain the Manuela ArgoCD location and log in

   `oc get -n manuela-ci routes/manuela-argocd-server`

1. Check all applications are synchronised

