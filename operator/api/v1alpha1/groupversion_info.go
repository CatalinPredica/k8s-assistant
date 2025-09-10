package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

// GroupName is the API group for the K8sAssistant CRD
const GroupName = "k8s-assistant.io"

// SchemeGroupVersion is group version used to register these objects
var SchemeGroupVersion = schema.GroupVersion{Group: GroupName, Version: "v1alpha1"}

// SchemeBuilder is used to add go types to the GroupVersionKind scheme
var SchemeBuilder = &scheme.Builder{GroupVersion: SchemeGroupVersion}

// AddToScheme adds all types of this clientset into the given scheme.
var AddToScheme = SchemeBuilder.AddToScheme

func init() {
	// Register the group version with the global scheme
	metav1.AddToGroupVersion(scheme.Scheme, SchemeGroupVersion)
}
