# Kubernetes-Kubesim : Distributed System Simulator 

A lightweight Kubernetes-style control plane simulator built using Flask and Docker. **KubernetesKubesim** supports node registration, heartbeat handling, pod scheduling, and node failure/recovery — all via a simple CLI and RESTful API.

---

## 📦 Clone the Repository

```bash
git clone https://github.com/your-username/KubernetesKubesim.git
cd KubernetesKubesim
```

## 🐳 Docker Setup
### Build the Docker Image

```bash
docker build -t kubernetes-kubesim .
```

### Run the Container
```bash
docker run -d -p 5001:5001 --name kube-cluster kubernetes-kubesim
```

### One-Time Run (No Container Saved)
```bash
docker run -it --rm -p 5001:5001 kubernetes-kubesim
```
###  Rebuild & Reset Easily
```bash
docker rm -f kube-cluster
docker build -t kubernetes-kubesim .
docker run -d -p 5001:5001 --name kube-cluster kubernetes-kubesim

```

### Persistent Storage (Volume Binding)
```bash
docker run -d -p 5001:5001 \
  -v $(pwd)/cluster.db:/app/cluster.db \
  --name kube-cluster kubernetes-kubesim
```

### Run the Simulator
```bash
python3 distributedsystems.py
```

## 🛠 CLI Commands (cli.py)

### List Nodes
```bash
python3 cli.py --list-nodes
```

###  Add a Node
```bash
python3 cli.py --add-node node1 6
```

### Launch a Pod
```bash
python3 cli.py --launch-pod pod1 2

```

### List All Pods
```bash
python3 cli.py --list-pods

```

### Simulate Node Failure
```bash
python3 cli.py --fail-node node1

```

### Recover Failed Node
```bash
python3 cli.py --recover-node node1

```

## 🌐 REST API Endpoints

### List Nodes

```bash
curl -X GET http://127.0.0.1:5001/list_nodes
```

### Add a Node
```bash
curl -X POST http://127.0.0.1:5001/add_node \
  -H "Content-Type: application/json" \
  -d '{"node_id": "node1", "cpu": 4}'

```


###  Send Heartbeat
```bash
curl -X POST http://127.0.0.1:5001/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"node_id": "node1"}'

```

### Launch a Pod
```bash
curl -X POST http://127.0.0.1:5001/launch_pod \
  -H "Content-Type: application/json" \
  -d '{"pod_id": "pod2", "cpu": 1}'

```
### Pod Resource Usage
```bash
curl http://127.0.0.1:5001/pod_usage

```

## ⏱ Automate Heartbeats

Use a simple script to simulate heartbeats:
```bash
while true; do
  curl -X POST http://127.0.0.1:5001/heartbeat \
    -H "Content-Type: application/json" \
    -d '{"node_id":"node1"}'
  sleep 5
done
```

## 🗂 Project Structure

```bash
KubernetesKubesim/
├── distributedsystems.py        # Main Flask application
├── cli.py                       # CLI tool for simulation
├── cluster.db                   # SQLite database
├── Dockerfile
├── README.md
└── requirements.txt
```














