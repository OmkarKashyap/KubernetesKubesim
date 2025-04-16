import requests
import argparse

BASE_URL = "http://127.0.0.1:5001"

def list_nodes():
    response = requests.get(f"{BASE_URL}/list_nodes")
    try:
        nodes = response.json()
        if isinstance(nodes, list):
            print("Node Status:")
            for node in nodes:
                print(f"Node ID: {node['node_id']}, CPU: {node['cpu']}, Last Heartbeat: {node['last_heartbeat']}, Status: {node['status']}")
        else:
            print("Unexpected response format:", nodes)
    except requests.exceptions.JSONDecodeError:
        print("Error retrieving nodes: Invalid JSON response.")

def list_pods():
    response = requests.get(f"{BASE_URL}/pod_usage")
    try:
        pods = response.json()
        if isinstance(pods, list):
            print("Pod Status:")
            for pod in pods:
                print(f"Pod ID: {pod['pod_id']}, CPU: {pod['cpu']}, Node: {pod['node_id']}, Status: {pod['status']}")
        else:
            print("Unexpected response format:", pods)
    except requests.exceptions.JSONDecodeError:
        print("Error retrieving pod information.")

def add_node(node_id, cpu):
    response = requests.post(f"{BASE_URL}/add_node", json={"node_id": node_id, "cpu": cpu})
    print(response.json())

def launch_pod(pod_id, cpu):
    response = requests.post(f"{BASE_URL}/launch_pod", json={"pod_id": pod_id, "cpu": cpu})
    print(response.json())

def fail_node(node_id):
    response = requests.post(f"{BASE_URL}/fail_node", json={"node_id": node_id})
    print(response.json())

def recover_node(node_id):
    response = requests.post(f"{BASE_URL}/recover_node", json={"node_id": node_id})
    print(response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for KubernetesKubesim")
    parser.add_argument("--list-nodes", action="store_true", help="List all nodes")
    parser.add_argument("--list-pods", action="store_true", help="List all pods")
    parser.add_argument("--add-node", nargs=2, metavar=("NODE_ID", "CPU"), help="Add a node with given CPU")
    parser.add_argument("--launch-pod", nargs=2, metavar=("POD_ID", "CPU"), help="Launch a pod with given CPU requirement")
    parser.add_argument("--fail-node", metavar="NODE_ID", help="Manually mark a node as failed")
    parser.add_argument("--recover-node", metavar="NODE_ID", help="Recover a previously failed node")

    args = parser.parse_args()

    if args.list_nodes:
        list_nodes()
    elif args.list_pods:
        list_pods()
    elif args.add_node:
        add_node(args.add_node[0], int(args.add_node[1]))
    elif args.launch_pod:
        launch_pod(args.launch_pod[0], int(args.launch_pod[1]))
    elif args.fail_node:
        fail_node(args.fail_node)
    elif args.recover_node:
        recover_node(args.recover_node)
