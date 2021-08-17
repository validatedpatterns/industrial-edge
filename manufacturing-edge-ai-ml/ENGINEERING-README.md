# Directory layout

## main/

The starting point for deploying the blueprint

## datacenter/

A directory of Helm charts deployed by ArgoCD on the datacenter

## datacenter/applications

An ArgoCD application that deploys all the other datacenter applications under `datacenter/` 

## factory/

WIP - needs to be updated to conform to the same pattern as `datacenter/` but for factory sites

## line/

Empty - needs to follow the same pattern as `datacenter/` but for factory's line servers

## gitops/

Imported from manuela-gitops, the content here needs to make its way into `datacenter/`, `factory/`, and `line/` as appropriate - or be removed
