# How to use

1. Fork this repo on GitHub 
1. Clone this repo  
   `git clone git@github.com:your-username/blueprints.git`
1. Create a local copy that includes credentials

  DO NOT COMMIT THIS FILE
   ```
   cp blueprints/manufacturing-edge-ai-ml/values.yaml blueprints/manufacturing-edge-ai-ml/secret-values.yaml
   vi blueprints/manufacturing-edge-ai-ml/values-secret.yaml
   ```

1. Preview the changes
   `cd blueprints/manufacturing-edge-ai-ml`
   `helm template manuela . --values values-secret.yaml --debug`
1. Apply it to your cluster
   `oc login`
   `helm install manuela . --values values-secret.yaml`
