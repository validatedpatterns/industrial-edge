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