from flask import Flask, request, jsonify
import threading
import time
import subprocess
import logging
import argparse

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

nodes = {}
pods = []
lock = threading.Lock()

def is_docker_running():
    docker_check = subprocess.run("docker info", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return docker_check.returncode == 0

def run_command(cmd):
    if not is_docker_running():
        logging.error(" Docker is not running! Please start Docker.")
        return
    
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd}\nError: {e.stderr.decode()}")

def create_docker_container(node_id):
    container_name = f"node_{node_id}"
    
    check_cmd = f"docker ps -a --filter 'name={container_name}' --format '{{{{.Names}}}}'"
    existing_container = subprocess.run(check_cmd, shell=True, capture_output=True, text=True).stdout.strip()
    
    if existing_container:
        logging.warning(f" Container '{container_name}' already exists. Removing it first...")
        remove_docker_container(node_id)  

    cmd = f"docker run -d --name {container_name} ubuntu sleep infinity"
    run_command(cmd)

def remove_docker_container(node_id):
    cmd = f"docker rm -f node_{node_id}"
    run_command(cmd)

def heartbeat_checker():
    while True:
        time.sleep(10)
        with lock:
            for node_id, node in list(nodes.items()):
                if time.time() - node['last_heartbeat'] > 30:
                    logging.warning(f" Node {node_id} failed! Removing node and rescheduling pods...")
                    failed_pods = node['pods'][:]
                    del nodes[node_id]
                    remove_docker_container(node_id)
                    reschedule_pods(failed_pods)

def reschedule_pods(failed_pods):
    """Try to reschedule pods from a failed node."""
    for pod_id, cpu_req in failed_pods:
        assigned_node = schedule_pod(pod_id, cpu_req, algorithm="best-fit")
        if assigned_node:
            logging.info(f"Pod {pod_id} rescheduled to Node {assigned_node}")
        else:
            pods.append((pod_id, cpu_req))  

def schedule_pod(pod_id, cpu_req, algorithm="first-fit"):
    best_node = None
    min_waste = float('inf')
    max_waste = -float('inf')

    with lock:
        for node_id, node in nodes.items():
            if node['cpu'] >= cpu_req:
                waste = node['cpu'] - cpu_req
                if algorithm == "first-fit":
                    best_node = node_id
                    break
                elif algorithm == "best-fit" and waste < min_waste:
                    min_waste = waste
                    best_node = node_id
                elif algorithm == "worst-fit" and waste > max_waste:
                    max_waste = waste
                    best_node = node_id
    
        if best_node:
            nodes[best_node]['pods'].append((pod_id, cpu_req))
            nodes[best_node]['cpu'] -= cpu_req
            return best_node
    return None

@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.json
    node_id = data['node_id']
    cpu = data['cpu']

    with lock:
        if node_id in nodes:
            return jsonify({'error': f'Node {node_id} already exists'}), 400

        nodes[node_id] = {
            'cpu': cpu,
            'pods': [],
            'last_heartbeat': time.time()
        }

    create_docker_container(node_id)
    
    return jsonify({'message': f' Node {node_id} added and Docker container launched'})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    node_id = data['node_id']
    with lock:
        if node_id in nodes:
            nodes[node_id]['last_heartbeat'] = time.time()
            return jsonify({'message': 'Heartbeat received'})
    return jsonify({'error': ' Node not found'}), 404

@app.route('/launch_pod', methods=['POST'])
def launch_pod():
    data = request.json
    pod_id = data['pod_id']
    cpu_req = data['cpu']
    assigned_node = schedule_pod(pod_id, cpu_req, algorithm="best-fit")  
    if assigned_node:
        return jsonify({'message': f' Pod {pod_id} launched on Node {assigned_node}'})
    return jsonify({'error': ' No available nodes'}), 400

@app.route('/list_nodes', methods=['GET'])
def list_nodes():
    """Returns the list of nodes with their status (Healthy/Unhealthy)."""
    with lock:
        current_time = time.time()
        node_statuses = {
            node_id: {
                'cpu': node['cpu'],
                'pods': node['pods'],
                'status': 'Healthy' if (current_time - node['last_heartbeat']) <= 30 else 'Unhealthy'
            } for node_id, node in nodes.items()
        }
    return jsonify(node_statuses)

def auto_heartbeat():
    while True:
        time.sleep(5)
        with lock:
            for node_id in nodes.keys():
                nodes[node_id]['last_heartbeat'] = time.time()

if __name__ == '__main__':
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    threading.Thread(target=auto_heartbeat, daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=True)
