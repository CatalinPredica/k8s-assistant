package v1alpha1

import (
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

const GroupName = "k8s-assistant.io"

var (
	// SchemeGroupVersion is group version used to register these objects
	SchemeGroupVersion = schema.GroupVersion{Group: GroupName, Version: "v1alpha1"}

	// SchemeBuilder is used to add go types to the GroupVersionKind scheme
	SchemeBuilder = &scheme.Builder{GroupVersion: SchemeGroupVersion}

	// AddToScheme adds all types of this clientset into the given scheme.
	AddToScheme = SchemeBuilder.AddToScheme
)

// Register the type with the SchemeBuilder
func init() {
	SchemeBuilder.Register(&K8sAssistant{}, &K8sAssistantList{})
}
