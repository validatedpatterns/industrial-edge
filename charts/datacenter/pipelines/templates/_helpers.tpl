{{/*
Set the hostname for the imageregistry if type is openshift-internal
*/}}
{{- define "imageRegistryHostname" -}}
{{- if (eq .Values.global.imageregistry.type "openshift-internal") -}}
registry.{{- .Values.global.hubClusterDomain -}}
{{- else }}
{{- .Values.global.imageregistry.hostname -}}
{{- end }}
{{- end }}

{{- define "imageRegistryAccount" -}}
{{- if (eq .Values.global.imageregistry.type "openshift-internal") -}}
ie-registry
{{- else }}
{{- .Values.global.imageregistry.account -}}
{{- end }}
{{- end }}

{{- define "build-base-images" -}}
- name: buildah-build
  taskRef:
    name: buildah
  runAfter:
    - git-clone-ops
    - git-clone-dev
  workspaces:
    - name: gitrepos
      workspace: gitrepos
    - name: config
      workspace: config
  params:
    - name: TLSVERIFY
      value: "false"
    - name: PATH_CONTEXT
      value: tekton/images/httpd-ionic
    - name: TAG
      value: latest
    - name: OUTPUT_IMAGE_PROVIDER_CONFIGMAPKEY
      value: IMAGE_PROVIDER
    - name: OUTPUT_IMAGE_ACCOUNT_CONFIGMAPKEY
      value: IMAGE_ACCOUNT
    - name: OUTPUT_IMAGE_NAME
      value: httpd-ionic
{{- end }} {{/* build-base-images */}}

{{- define "build-iot-component" }}
- name: bump-build-version-{{ .component.component_name }}
  displayName: "Bump version for {{ .component.component_name }}"
  taskRef:
    name: bumpversion
  runAfter:
  - git-clone-ops
  - git-clone-dev
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  params:
  - name: component_name
    value: {{ .component.component_name }}
  - name: version_file_path
    value: components/{{ .component.component_name }}/VERSION

- name: s2i-build-{{ .component.component_name }}
  displayName: "S2I build IoT {{ .component.component_name }}"
  taskRef:
    name: s2i
  runAfter:
  - bump-build-version-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: build-artifacts
    workspace: build-artifacts
  params:
  - name: TLSVERIFY
    value: "false"
  - name: PATH_CONTEXT
    value: components/{{ .component.component_name }}
  - name: BUILDER_IMAGE
    value: {{ .component.builder_image }}
  {{- if .component.chained_build_dockerfile }}
  - name: CHAINED_BUILD_DOCKERFILE
    value: {{ .component.chained_build_dockerfile }}
  {{- end }}
  - name: TAG
    value: $(tasks.bump-build-version-{{ .component.component_name }}.results.image-tag)
  - name: OUTPUT_IMAGE
    value: image-registry.openshift-image-registry.svc:5000/manuela-tst-all/{{ .component.output_image_name }}

- name: copy-image-to-remote-registry-{{ .component.component_name }}
  displayName: "Copy image to remote registry"
  taskRef:
    name: skopeo-copy
  runAfter:
  - s2i-build-{{ .component.component_name }}
  workspaces:
  - name: config
    workspace: config
  params:
  - name: TAG
    value: $(tasks.bump-build-version-{{ .component.component_name }}.results.image-tag)
  - name: SOURCE_IMAGE
    value: image-registry.openshift-image-registry.svc:5000/manuela-tst-all/{{ .component.output_image_name }}
  - name: TARGET_IMAGE_CONFIGMAPKEY
    value: {{ .component.configmap_prefix }}_IMAGE

- name: push-dev-tag-{{ .component.component_name }}
  taskRef:
    name: github-push
  runAfter:
  - copy-image-to-remote-registry-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  params:
  - name: PUSH_FLAGS
    value: --tags

- name: modify-ops-test-iot-component-{{ .component.component_name }}
  taskRef:
    name: gitops-imagetag
  runAfter:
  - push-dev-tag-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: config
    workspace: config
  params:
  - name: CONFIGMAP_PREFIX
    value: {{ .component.configmap_prefix }}
  - name: ENVIRONMENT
    value: TEST
  - name: TAG
    value: $(tasks.bump-build-version-{{ .component.component_name }}.results.image-tag)
  - name: subdirectory
    value: ops

- name: modify-ops-prod-iot-component-{{ .component.component_name }}
  when:
    - input: "{{ .seed_prod }}"
      operator: in
      values: ["true"]
  taskRef:
    name: gitops-imagetag
  runAfter:
  - modify-ops-test-iot-component-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: config
    workspace: config
  params:
  - name: CONFIGMAP_PREFIX
    value: {{ .component.configmap_prefix }}
  - name: ENVIRONMENT
    value: PROD
  - name: TAG
    value: $(tasks.bump-build-version-{{ .component.component_name }}.results.image-tag)
  - name: subdirectory
    value: ops

- name: commit-ops-{{ .component.component_name }}
  taskRef:
    name: git-commit
  runAfter:
  - modify-ops-prod-iot-component-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: config
    workspace: config
  params:
  - name: subdirectory
    value: ops

- name: push-ops-{{ .component.component_name }}
  taskRef:
    name: github-push
  runAfter:
  - commit-ops-{{ .component.component_name }}
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  params:
  - name: subdirectory
    value: ops
  - name: PUSH_FLAGS
    value: --all
{{- end }} {{/* build-iot-component */}}

{{- define "test-all" }}
- name: sensor-broker-test
  taskRef:
    name: mock
    kind: Task
  runAfter:
    - argocd-sync-application
  params:
    - name: MESSAGE
      value: "succesfully sent messages to broker..."
- name: consumer-broker-test
  taskRef:
    name: mock
    kind: Task
  runAfter:
    - argocd-sync-application
  params:
    - name: MESSAGE
      value: "succesfully processed messages from broker..."
- name: consumer-frontend-test
  taskRef:
    name: mock
    kind: Task
  runAfter:
    - argocd-sync-application
  params:
    - name: MESSAGE
      value: "succesfully executed Websocket APIs..."
- name: e2e-test
  taskRef:
    name: mock
    kind: Task
  runAfter:
    - sensor-broker-test
    - consumer-broker-test
    - consumer-frontend-test
  params:
    - name: MESSAGE
      value: "e2e testsuite succesfully executed"
{{- end }}

{{- define "trigger-staging" }}
- name: checkout-staging-branch
  taskRef:
    name: git-checkout
  runAfter:
  -  e2e-test
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  params:
  - name: subdirectory
    value: ops
  - name: BRANCH
    value: staging-approval
  - name: STARTINGBRANCH
    value: {{ .root.global.targetRevision }}
- name: modify-ops-prod
  taskRef:
    name: gitops-imagetag
  runAfter:
  - checkout-staging-branch
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: config
    workspace: config
  params:
  - name: CONFIGMAP_PREFIX
    value: {{ .component.configmap_prefix }}
  - name: ENVIRONMENT
    value: PROD
  - name: TAG
    value: $(tasks.bump-build-version-{{ .component.component_name }}.results.image-tag)
  - name: subdirectory
    value: ops
- name: commit-ops-prod
  taskRef:
    name: git-commit
  runAfter:
  - modify-ops-prod
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  - name: config
    workspace: config
  params:
  - name: subdirectory
    value: ops
- name: push-ops-prod
  taskRef:
    name: github-push
  runAfter:
  - commit-ops-prod
  workspaces:
  - name: gitrepos
    workspace: gitrepos
  params:
  - name: subdirectory
    value: ops
  - name: PUSH_FLAGS
    value: --set-upstream origin staging-approval -f
- name: github-pull-request
  taskRef:
    name: github-add-pull-request
  runAfter:
  - push-ops-prod
  workspaces:
  - name: config
    workspace: config
  - name: github-secret
    workspace: github-secret
  params:
  - name: GITHUB_REPO_CONFIGMAPKEY
    value: GIT_OPS_REPO_PROD_URL
  - name: GIT_BRANCH_HEAD
    value: staging-approval
  - name: GIT_BRANCH_BASE
    value: {{ .root.global.targetRevision }}
{{- end }}