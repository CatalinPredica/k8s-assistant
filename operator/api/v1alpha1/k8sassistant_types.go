package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type K8sAssistantSpec struct {
	Version         string `json:"version"`
	ApiKeySecretRef string `json:"apiKeySecretRef"`
	Replicas        struct {
		Frontend int32 `json:"frontend"`
		Backend  int32 `json:"backend"`
	} `json:"replicas"`
}

type K8sAssistantStatus struct {
	Phase       string `json:"phase,omitempty"`
	FrontendURL string `json:"frontendURL,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type K8sAssistant struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   K8sAssistantSpec   `json:"spec,omitempty"`
	Status K8sAssistantStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
type K8sAssistantList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []K8sAssistant `json:"items"`
}
