from kubernetes import client, config
from typing import Dict, Any
import os

# Load in-cluster config if present, else local kubeconfig (dev)
if os.getenv("KUBERNETES_SERVICE_HOST"):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()
apps = client.AppsV1Api()
metrics_available = False

# Optional: metrics
try:
    from kubernetes.client import CustomObjectsApi
    k8s_custom = CustomObjectsApi()
    metrics_available = True
except Exception:
    metrics_available = False

SAFE_RESOURCES = {"namespaces", "pods", "nodes", "services", "deployments", "events"}
SAFE_ACTIONS   = {"get", "describe", "logs", "top"}

async def execute(intent: Dict[str, Any]) -> Dict[str, Any]:
    action = intent.get("action", "get")
    resource = intent.get("resource", "pods")
    ns = intent.get("namespace")
    extras = intent.get("extras", {})

    if action not in SAFE_ACTIONS or resource not in SAFE_RESOURCES:
        return {"error": "Disallowed action/resource", "intent": intent}

    if action == "get":
        if resource == "namespaces":
            items = core.list_namespace().items
            return {"items": [i.metadata.name for i in items]}
        if resource == "pods":
            ns = ns or "default"
            items = core.list_namespaced_pod(ns).items
            return {"items": [p.metadata.name for p in items]}
        if resource == "services":
            ns = ns or "default"
            items = core.list_namespaced_service(ns).items
            return {"items": [s.metadata.name for s in items]}
        if resource == "nodes":
            items = core.list_node().items
            return {"items": [n.metadata.name for n in items]}
        if resource == "deployments":
            ns = ns or "default"
            items = apps.list_namespaced_deployment(ns).items
            return {"items": [d.metadata.name for d in items]}
        if resource == "events":
            ns = ns or "default"
            items = core.list_namespaced_event(ns).items
            return {"items": [f"{e.last_timestamp} {e.involved_object.kind}/{e.involved_object.name}: {e.message}" for e in items]}

    if action == "logs" and resource == "pods":
        ns = ns or "default"
        pod = extras.get("pod")
        if not pod:
            return {"error": "pod required for logs"}
        log = core.read_namespaced_pod_log(name=pod, namespace=ns, tail_lines=int(extras.get("tail", 200)))
        return {"log": log}

    if action == "top":
        if not metrics_available:
            return {"error": "metrics API not available (deploy metrics-server)"}
        # Example for nodes metrics via metrics.k8s.io (requires metrics-server)
        try:
            metrics = k8s_custom.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
            items = [f"{i['metadata']['name']} CPU {i['usage']['cpu']} MEM {i['usage']['memory']}" for i in metrics.get('items', [])]
            return {"items": items}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Unsupported intent", "intent": intent}