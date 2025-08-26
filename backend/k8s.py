import os
import logging
from typing import Dict, Any
from kubernetes import client, config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load in-cluster config if present, else local kubeconfig (dev)
if os.getenv("KUBERNETES_SERVICE_HOST"):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()
apps = client.AppsV1Api()
metrics_available = False

# Optional metrics API
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
    all_namespaces = intent.get("all_namespaces", False)
    extras = intent.get("extras", {})
    name = intent.get("name")  # For logs or single resources

    if action not in SAFE_ACTIONS or resource not in SAFE_RESOURCES.union({"pod"}):
        return {"error": "Disallowed action/resource", "intent": intent}

    try:
        if action == "get":
            if resource == "namespaces":
                items = core.list_namespace().items
                return {"items": [i.metadata.name for i in items]}

            if resource in ("pods", "pod"):
                def format_pod(pod_obj, ns_name):
                    phase = pod_obj.status.phase or "Unknown"
                    return f"{ns_name}/{pod_obj.metadata.name} ({phase})"

                if all_namespaces:
                    all_pods = []
                    namespaces = core.list_namespace().items
                    for ns_obj in namespaces:
                        ns_name = ns_obj.metadata.name
                        try:
                            pods = core.list_namespaced_pod(ns_name).items
                            for pod in pods:
                                all_pods.append(format_pod(pod, ns_name))
                        except Exception:
                            continue
                    return {"items": all_pods, "all_namespaces": True}
                else:
                    ns = ns or "default"
                    items = core.list_namespaced_pod(ns).items
                    return {"items": [format_pod(p, ns) for p in items], "namespace": ns}

            if resource == "services":
                if all_namespaces:
                    all_services = []
                    namespaces = core.list_namespace().items
                    for ns_obj in namespaces:
                        ns_name = ns_obj.metadata.name
                        try:
                            services = core.list_namespaced_service(ns_name).items
                            for service in services:
                                all_services.append(f"{ns_name}/{service.metadata.name}")
                        except Exception:
                            continue
                    return {"items": all_services, "all_namespaces": True}
                else:
                    ns = ns or "default"
                    items = core.list_namespaced_service(ns).items
                    return {"items": [s.metadata.name for s in items], "namespace": ns}

            if resource == "deployments":
                if all_namespaces:
                    all_deployments = []
                    namespaces = core.list_namespace().items
                    for ns_obj in namespaces:
                        ns_name = ns_obj.metadata.name
                        try:
                            deployments = apps.list_namespaced_deployment(ns_name).items
                            for deployment in deployments:
                                all_deployments.append(f"{ns_name}/{deployment.metadata.name}")
                        except Exception:
                            continue
                    return {"items": all_deployments, "all_namespaces": True}
                else:
                    ns = ns or "default"
                    items = apps.list_namespaced_deployment(ns).items
                    return {"items": [d.metadata.name for d in items], "namespace": ns}

            if resource == "nodes":
                items = core.list_node().items
                return {"items": [n.metadata.name for n in items]}

            if resource == "events":
                if all_namespaces:
                    all_events = []
                    namespaces = core.list_namespace().items
                    for ns_obj in namespaces:
                        ns_name = ns_obj.metadata.name
                        try:
                            events = core.list_namespaced_event(ns_name).items
                            for event in events:
                                all_events.append(f"{ns_name}: {event.last_timestamp} {event.involved_object.kind}/{event.involved_object.name}: {event.message}")
                        except Exception:
                            continue
                    return {"items": all_events, "all_namespaces": True}
                else:
                    ns = ns or "default"
                    items = core.list_namespaced_event(ns).items
                    return {"items": [f"{e.last_timestamp} {e.involved_object.kind}/{e.involved_object.name}: {e.message}" for e in items], "namespace": ns}

        if action == "logs" and resource in ("pod", "pods"):
            ns = ns or "default"
            pod = name or extras.get("pod")
            if not pod:
                return {"error": "pod required for logs"}
            container = extras.get("container")  # optional
            tail = int(extras.get("tail", 200))
            try:
                log = core.read_namespaced_pod_log(
                    name=pod,
                    namespace=ns,
                    container=container,
                    tail_lines=tail
                )
                return {"log": log, "pod": pod, "namespace": ns}
            except client.exceptions.ApiException as e:
                logger.error(f"Kubernetes API error reading logs for pod {pod} in {ns}: {e}")
                return {"error": f"Kubernetes API error: {e.reason}", "code": e.status}
            except Exception as e:
                logger.error(f"Unexpected error reading logs for pod {pod} in {ns}: {e}")
                return {"error": f"Unexpected error reading logs: {str(e)}"}

        if action == "top":
            if not metrics_available:
                return {"error": "metrics API not available (deploy metrics-server)"}
            try:
                metrics = k8s_custom.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
                items = [f"{i['metadata']['name']} CPU {i['usage']['cpu']} MEM {i['usage']['memory']}" for i in metrics.get('items', [])]
                return {"items": items}
            except Exception as e:
                return {"error": str(e)}

        return {"error": "Unsupported intent", "intent": intent}

    except Exception as e:
        logger.error(f"Unexpected error in execute(): {e}")
        return {"error": f"Unexpected error: {str(e)}", "intent": intent}