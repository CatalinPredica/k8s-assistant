


Installation ok k8s-assistant with operator:

kubectl apply -f operator/operator-bootstrap.yaml

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

Access k8s-assistant Web-UI:
kubectl port-forward service/my-assistant-k8s-assistant-frontend 8080:80 -n k8s-assistant