# Tekton Pipelines (reworked) <!-- omit in toc -->

- [Design Considerations](#design-considerations)
- [Pipelines](#pipelines)
- [How to start a pipeline](#how-to-start-a-pipeline)
- [Versioning and Tagging](#versioning-and-tagging)
- [Storing build artifacts across builds](#storing-build-artifacts-across-builds)
- [Open issues](#open-issues)

## Technical Debt

This whole directory should be considered technical debt.

It works, for now, but we need to either use
[kam](https://github.com/redhat-developer/kam/) from the openshift-pipelines folks, or
investigate and replicate the best-practice patterns it creates.

In the same way that values-datacenter.yaml has a list of `applications:`, we
want to provide similar templating for "I have a repository with a Dockerfile I need
to build and use"

## Design Considerations

These pipelines are designed to be long, with simple reusable tasks. They do not use PipelineResources due to the unclear nature of their future. Instead, they use tasks, workspaces and persistent volume claims to achieve similar goals: Clone the repositories, build the code, deploy to test, test and then trigger a staging to production. For each component, there is a separate PVC to allow parallel component builds without two pipeline runs stepping on each others toes. In the future (post Tekton-v0.11), the PVCs can be created on the fly instead of having to be static. The Git clone tasks clone their repositories into a subdirectory of this PVC, so both the dev and ops repositories reside on the same PVC.

The build-and-test pipeline is designed to be generic in nature and to be used on all components. In the previous attempt to provide pipelines, all component pipelines were the same instead of the build step which used a component specific s2i task. This design can be deviated from in the future if need arises to provide a component-specific pipeline. There is a certain amount of logic within the s2i task to distinguish java-based s2i builds from others since the former require some special handling, such as setting up the Maven environment and special parameters to the s2i build process.

All tasks are simple and designed not to have any hardwired dependencies, such as a direct reference to a configmap or secret, or implicit dependencies such as secrets added to the pipeline user. This means that all these dependencies are provided as Tekton workspaces, which are passed from the Tekton Pipeline(Run) to the Task(Run). This enables to reuse the same task across different environments, such as different GitHub users, Quay Repositories, etc. A drawback of this approach is that in the current state of OpenShift Pipelines UI (v0.11), these pipelines can no longer be instantiated via UI, since it doesn't provide a UI to define workspaces. To allow developers to instantiate PipelineRuns, OpenShift Templates are provided which instantiate a component PipelineRun with a name indicating which Component is being built.

Tasks are named to indicate whether they are specific to a certain product, such as OpenShift or GitHub. This should allow to identify which tasks need to be adjusted if this demo is ported to other scnearios.

Another design goal was to put all environment-specific configuration into a (single) ConfigMap, to allow easy reconfiguration of the Pipeline for new environments. It contains both global configuration (such as the location of the dev and ops Git repositories) as well as component-specific configuration items whose key is prefixed with a component-specific name, such as IOT_CONSUMER_. This way, the whole pipeline can be reused for different components, just by specifying the component prefix.

## Pipelines

There are four pipelines:

- [build-and-test](pipelines/build-and-test.yaml): this pipeline performs a checkout of the Git dev and ops repos, and determines the next build tag. It then triggers an s2i build and the gitops modifications to deploy the new version for testing in parallel. If the s2i build completes successfully, the new build version tag is pushed to the dev repository, and the ops modifications to the ops repository. After syncing the test instance through ArgoCD, it tiggers the [test-all](pipelines/test-all.yaml) pipeline and waits for its completion. Once completed, it triggers the [stage-production](pipelines/stage-production.yaml) pipeline and cleans up excess tags in the Git repository.

- [test-all](pipelines/test-all.yaml): this pipeline is a sequence of (currently mocked) component tests and integration tests.

- [stage-production](pipelines/stage-production.yaml): checks out the Git ops repository and switches to a branch "staging-approval". If this branch does not exist, it is created. It then modifies the Git ops repository for the production deployment and commits and pushes the changes to the origin ops repo's staging-approval branch. Finally, it creates a pull-request from the origin repo's staging-approval to the origin master branch, if no pull request is pending.

- [seed](pipelines/seed.yaml): checks out the Git dev and ops repositories and builds all components in parallel. It modifies the ops repositories for both test and prod on the master branch and pushes these changes to origin. This pipeline is useful to prepare a new installation to a known good state on which demo runs can take place.

## How to start a pipeline

The pipelines expect a set of parameters and workspaces to be in place. To make it easier to create such PipelineRuns, there are a number of OpenShift templates. These templates contain all the required configuration and ensure the PipelineRuns contain the name of the component in question:

- [build-iot-consumer](templates/build-iot-consumer.yaml): Start the pipeline for the iot-consumer component
- [build-iot-frontend](templates/build-iot-frontend.yaml): Start the pipeline for the iot-frontend component
- [build-iot-software-sensor](templates/build-iot-software-sensor.yaml): Start the pipeline for the iot-software-sensor component
- [seed](templates/seed.yaml): Start the pipeline to seed the environment

They can be instantiated as follows:

```bash
oc process -n manuela-ci build-iot-consumer | oc process -n manuela-ci -f -
```

In addition, there is a [stage-production-pipelinerun](templates/stage-production-pipelinerun.yaml) template which is used by the [build-and-test](pipelines/build-and-test.yaml) pipeline to trigger the [stage-production](pipelines/stage-production.yaml) pipeline.

## Versioning and Tagging

These pipelines use Git tags in the dev repository to maintain the state which build number is current per component. The task [bumpversion](tasks/bumpversion.yaml) retrieves the component version from its VERSION file in the dev repository. It then searches for the highest tag matching "build-COMPONENTNAME-VERSION-*". In case it doesn't find one, it assumes "build-COMPONENTNAME-VERSION-0". The task then increases the build number (after the last dash) and tags the repository accordingly to form a tag in the form "build-COMPONENTNAME-VERSION-BUILD". These tags can be pushed to origin in a later task.

OCI Images are tagged with "VERSION-BUILD" since the component name is already reflected in the image name.

## Storing build artifacts across builds

The pipelines use the PVC ```build-artifacts``` to store build artifacts (such as maven cache) across pipeline runs and component builds. If you want to clear this cache, delete and recreate the PVC.

## Open issues

- A failure in the [test-all](pipelines/test-all.yaml) pipeline does not cause the [build-and-test](pipelines/build-and-test.yaml) pipeline to fail.

- A rerun of a pipeline run is launched with a generic name, i.e. without the component name.

- The VERSION of a component should only be increased, never decreased. Otherwise the clenaup task will remove the wrong tags, since it tries to keep the "highest" version tags.
