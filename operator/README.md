


Installation ok k8s-assistant with operator:


kubectl apply -f config/manager/manager.yaml

kubectl apply -f config/rbac/service_account.yaml
kubectl create clusterrolebinding operator-admin --clusterrole=cluster-admin --serviceaccount=operator:controller-manager


CRD

kubectl apply -f - <<EOF
apiVersion: apps.catalin.dev/v1alpha1
kind: K8sAssistant
metadata:
  name: my-assistant
  namespace: k8s-assistant
spec:
  version: "0.2.41"
  secret:
    apiKey: "Your-Gemini-API-Key"
  replicas:
    frontend: 1
    backend: 1
EOF

