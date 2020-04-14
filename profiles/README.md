This folder contains deployment profiles as overlays on top of the base layer.

A profile should be used to adapt the base layer to a specific platform (e.g. add AWS-specific attributes), stage (e.g. only use one master in testing stage), or version (e.g. override manifest API version to adapt to different openshift-installer versions).

By convention, profiles should be named "<stage>[-<version>].<platform>". Each profile must have an entry in requirements.yaml with a key corresponding to the profile name.