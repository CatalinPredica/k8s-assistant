{{/*
Return the name of the chart
*/}}
{{- define "k8s-assistant.name" -}}
{{- .Chart.Name | trim -}}
{{- end -}}

{{/*
Return the full name of the release
*/}}
{{- define "k8s-assistant.fullname" -}}
{{- printf "%s-%s" (.Release.Name | trim) (.Chart.Name | trim) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Return the service account name
*/}}
{{- define "k8s-assistant.serviceAccountName" -}}
{{- if .Values.serviceAccount.name }}
{{- .Values.serviceAccount.name | trim -}}
{{- else }}
{{- include "k8s-assistant.fullname" . | trim }}-sa
{{- end -}}
{{- end -}}