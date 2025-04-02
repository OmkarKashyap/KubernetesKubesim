import requests
import argparse

BASE_URL = "http://127.0.0.1:5001"

def add_node(node_id, cpu):
    response = requests.post(f"{BASE_URL}/add_node", json={"node_id": node_id, "cpu": cpu})
    print(response.json())

def launch_pod(pod_id, cpu):
    response = requests.post(f"{BASE_URL}/launch_pod", json={"pod_id": pod_id, "cpu": cpu})
    print(response.json())

def list_nodes():
    response = requests.get(f"{BASE_URL}/list_nodes")
    print(response.json())

parser = argparse.ArgumentParser(description="CLI for Distributed Systems Cluster")
parser.add_argument("--add-node", nargs=2, metavar=("NODE_ID", "CPU"), help="Add a node with given CPU cores")
parser.add_argument("--launch-pod", nargs=2, metavar=("POD_ID", "CPU"), help="Launch a pod with required CPU")
parser.add_argument("--list-nodes", action="store_true", help="List all nodes")

args = parser.parse_args()

if args.add_node:
    add_node(args.add_node[0], int(args.add_node[1]))
elif args.launch_pod:
    launch_pod(args.launch_pod[0], int(args.launch_pod[1]))
elif args.list_nodes:
    list_nodes()
