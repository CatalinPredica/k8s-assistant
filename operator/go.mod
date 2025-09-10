module github.com/catalinpredica/k8s-assistant/operator

go 1.23

require (
	// Controller-runtime for controller scaffolding
	sigs.k8s.io/controller-runtime v0.22.1

	// Helm SDK (v3)
	helm.sh/helm/v3 v3.18.6
)