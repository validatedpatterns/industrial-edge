# How to use

1. Fork this repo on GitHub 
1. Clone this repo  
   `git clone git@github.com:your-username/blueprints.git`
1. Change the defaults
   `vi blueprints/manufacturing-edge-ai-ml/values.yaml`
   `git commit -m "Supply Git and Quay locations"`
   `git push`
1. Create a local copy that includes credentials  
   `cp blueprints/manufacturing-edge-ai-ml/values.yaml blueprints/manufacturing-edge-ai-ml/secret-values.yaml`
   `vi blueprints/manufacturing-edge-ai-ml/secret-values.yaml`
1. Preview the changes
   `cd blueprints/manufacturing-edge-ai-ml`
   `helm template manuela . --values secret-values.yaml --post-renderer kustomize/kustomize --debug`
1. Apply it to your cluster
   `oc login`
   `helm install manuela . --values secret-values.yaml --post-renderer kustomize/kustomize --debug`
1. Work-around... repeat the previous step until there are no error
