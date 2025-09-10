package controllers

import (
	"context"
	"fmt"

	appv1alpha1 "github.com/catalinpredica/k8s-assistant/operator/api/v1alpha1"
	"helm.sh/helm/v3/pkg/action"
	"helm.sh/helm/v3/pkg/chart/loader"
	"helm.sh/helm/v3/pkg/cli"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type K8sAssistantReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

func (r *K8sAssistantReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	var instance appv1alpha1.K8sAssistant
	if err := r.Get(ctx, req.NamespacedName, &instance); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	cfg := new(action.Configuration)
	if err := cfg.Init(cli.New().RESTClientGetter(), req.Namespace, "secret", func(format string, v ...interface{}) {}); err != nil {
		return ctrl.Result{}, err
	}

	chartPath := "https://catalinpredica.github.io/k8s-assistant/charts/k8s-assistant"
	chart, err := loader.Load(chartPath)
	if err != nil {
		return ctrl.Result{}, err
	}

	values := map[string]interface{}{
		"secret": map[string]interface{}{
			"apiKey": instance.Spec.ApiKeySecretRef,
		},
		"replicas": map[string]interface{}{
			"frontend": instance.Spec.Replicas.Frontend,
			"backend":  instance.Spec.Replicas.Backend,
		},
		"image": map[string]interface{}{
			"tag": instance.Spec.Version,
		},
	}

	upgrade := action.NewUpgrade(cfg)
	upgrade.Namespace = req.Namespace
	_, err = upgrade.Run(req.Name, chart, values)
	if err != nil {
		install := action.NewInstall(cfg)
		install.ReleaseName = req.Name
		install.Namespace = req.Namespace
		if _, err := install.Run(chart, values); err != nil {
			return ctrl.Result{}, err
		}
		instance.Status.Phase = "Installed"
	} else {
		instance.Status.Phase = "Upgraded"
	}

	instance.Status.FrontendURL = fmt.Sprintf("http://%s-frontend.%s.svc.cluster.local",
		req.Name, req.Namespace)

	if err := r.Status().Update(ctx, &instance); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

func (r *K8sAssistantReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&appv1alpha1.K8sAssistant{}).
		Complete(r)
}
