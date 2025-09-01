# Kubernetes Assistant

The latest release is [0.2.10](https://github.com/CatalinPredica/k8s-assistant/releases/tag/0.2.10)

An AI-powered Web Assistant for Kubernetes clusters that lets you query and interact with your cluster in natural language:
(e.g., “what pods are failing in operations?”), executes them against the cluster, and returns formatted answers.

Deployable with Helm into any AKS/EKS (or vanilla k8s). This project consists of **two main components** deployed as containers via Helm:

1. **Backend**: Python FastAPI service integrating Gemini AI for reasoning and command generation.
2. **Frontend**: React-based dashboard for user interaction.

---

## Features

- **Natural language queries** → AI generates Kubernetes commands and interprets results.
- **Backend**: Python + FastAPI + Gemini AI model.
- **Frontend**: React app for interactive web UI.
- **Helm deployment** → Easily deploy both components on any Kubernetes cluster.
- **RBAC & ServiceAccount** → Secure access to Kubernetes API.
- **Secret management** → Users provide their own Gemini API key; not stored in repo.

---

## Architecture

[User] —> [React Frontend] —> [Python Backend / FastAPI] —> [Kubernetes Cluster]
(Gemini AI reasoning)

- Frontend communicates with backend via API.
- Backend interacts with the Kubernetes API and uses Gemini AI to interpret queries.
- Each component runs in its own container.

**Key Points in this Workflow**

1. Backend never interprets intent, only executes kubectl_command and maintains step structure.
2. AI only decides intent & next action — never manipulates YAML structure.
	- What command(s) to run.
	- When to populate final_output.
3. Empty steps are created by backend for AI to fill if needed — ensures flexibility for multi-step reasoning.
4. Single loop is enough for simple queries, multiple loops will be needed for complex issues (e.g., CrashLoopBackOff).
5. Loops continue until final_output is populated — AI decides when reasoning is complete.

**Robust design:**

- You never trust AI with YAML formatting → schema is always correct.
- AI has full context of previous steps → can make intelligent multi-step decisions.
- Backend can audit every command executed → important for security.
- New types of queries or resources can be handled without hardcoding additional logic in backend.
 
---

## Prerequisites

- Kubernetes cluster (v1.24+ recommended)
- Helm v3+
- Python 3.10+ for local backend testing (optional)
- Gemini AI API key (must be provided)

---

## Installation

  1. Add the Helm repo:

```bash
helm repo add k8s-assistant https://catalinpredica.github.io/k8s-assistant/charts
helm repo update
```

  2. Create a file values.secret.yaml with your Gemini API key:

```yaml
secret:
  apiKey: "YOUR_REAL_API_KEY"
```

  3. Deploy with Helm from the repo:

```bash
helm install k8s-assistant-release k8s-assistant/k8s-assistant --namespace k8s-assistant -f helm/values.secret.yaml
```

  4. Upgrade an existing release

```bash
helm repo update
helm upgrade k8s-assistant-release k8s-assistant/k8s-assistant --namespace k8s-assistant -f helm/values.secret.yaml
```

Helm will fail if apiKey is not provided, enforcing secure deployment.

## Components
⸻

Frontend: Deployemnt and Service

- React + Vite application
- Communicates with backend via /api endpoints
- Can be deployed via Helm along with backend
- Supports markdown response rendering

⸻

Backend: Deployment and Service

- Python FastAPI service
- Uses Kubernetes Python client to interact with cluster
- Integrates Gemini AI for reasoning
- Exposes /api/ask endpoint for frontend queries
- Logs structured data for debugging

⸻

Security Considerations: ClusterRoleBinding, ServiceAccount and Secret

- RBAC enabled to ensure least-privilege access
- ServiceAccount is created specifically for this application
- Secrets managed via Kubernetes Secret object
- API keys never stored in repo

⸻

## Contributing

Contributions welcome!

- Open issues for bugs or feature requests
- Submit pull requests for improvements
- Follow Helm best practices and maintain secret handling

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
