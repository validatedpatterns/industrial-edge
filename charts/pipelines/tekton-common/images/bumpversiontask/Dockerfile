FROM registry.access.redhat.com/ubi8/ubi-minimal
#Work around https://github.com/tektoncd/pipeline/issues/2131
#USER root
RUN  microdnf -y install python3 \
  && microdnf clean all -y \
  && pip3 install --upgrade bump2version
