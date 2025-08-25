## Natural‑Language Kubernetes ops

AI‑assisted Web dashboard that turns human commands into safe Kubernetes queries (e.g., “what pods are failing in operations?”), executes them against the cluster, and returns formatted answers. Deployable with Helm into any AKS/EKS (or vanilla k8s).

## Repo structure

k8s-assistant/
├─ helm/
│  ├─ Chart.yaml
│  ├─ values.yaml
│  └─ templates/
│     ├─ deployment-backend.yaml
│     ├─ deployment-frontend.yaml
│     ├─ service-backend.yaml
│     ├─ service-frontend.yaml
│     ├─ ingress.yaml
│     ├─ serviceaccount.yaml
│     ├─ clusterrole.yaml
│     ├─ clusterrolebinding.yaml
│     ├─ configmap.yaml
│     ├─ secret.yaml
│     └─ networkpolicy.yaml
├─ backend/
│  ├─ app.py
│  ├─ k8s.py
│  ├─ ai.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.ts
│  ├─ index.html
│  └─ Dockerfile
│  └─ src/
│     ├─ main.tsx
│     └─ App.tsx
└─ README.md


# Backend (Python FastAPI)

Goals:
Expose /api/ask that accepts a user prompt.
Call Ollama (local LLM) over HTTP inside the cluster.
Translate NL → safe kubectl intents (whitelist), execute via Kubernetes Python client under a dedicated ServiceAccount with read-only RBAC.
Return structured JSON (answer, raw command, raw data).

## build, tag, and push them to your DockerHub (catalinpredica) with both 0.1.1 and latest tags

# Backend image in catalinpredica/k8s-assistant-backend docker repo
# cd into backend folder
cd backend

# build image
docker build -t catalinpredica/k8s-assistant-backend:0.1.1 -t catalinpredica/k8s-assistant-backend:latest .

# push both tags
docker push catalinpredica/k8s-assistant-backend:0.1.1
docker push catalinpredica/k8s-assistant-backend:latest

# Frontend image in catalinpredica/k8s-assistant-frontend docker repo
# cd into frontend folder
cd frontend

# build image
docker build -t catalinpredica/k8s-assistant-frontend:0.1.1 -t catalinpredica/k8s-assistant-frontend:latest .

# push both tags
docker push catalinpredica/k8s-assistant-frontend:0.1.1
docker push catalinpredica/k8s-assistant-frontend:latest

helm upgrade test-release ./helm



cd backend
docker build -t catalinpredica/k8s-assistant-backend:0.3.6 .
docker push catalinpredica/k8s-assistant-backend:0.3.6
cd ..
helm upgrade test-release ./helm

cd frontend
docker build -t catalinpredica/k8s-assistant-frontend:0.1.9 .
docker push catalinpredica/k8s-assistant-frontend:0.1.9
cd ..
helm upgrade test-release ./helm

