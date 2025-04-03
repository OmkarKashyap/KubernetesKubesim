from flask import Flask, request, jsonify
import threading
import time
import subprocess
import logging
import sqlite3

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

db_file = "cluster.db"
lock = threading.Lock()

# Initialize Database
def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                cpu INTEGER,
                last_heartbeat REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pods (
                pod_id TEXT PRIMARY KEY,
                cpu INTEGER,
                node_id TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (node_id) REFERENCES nodes (node_id)
            )
        """)
        conn.commit()
init_db()

def run_command(cmd):
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def auto_reschedule():
    while True:
        time.sleep(15)
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pod_id, cpu FROM pods WHERE node_id IS NULL")
            failed_pods = cursor.fetchall()
            for pod_id, cpu in failed_pods:
                assigned_node = schedule_pod(pod_id, cpu)
                if assigned_node:
                    logging.info(f"Rescheduled pod {pod_id} to Node {assigned_node}")

def schedule_pod(pod_id, cpu_req):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT node_id, cpu FROM nodes ORDER BY cpu DESC")
        nodes = cursor.fetchall()
        
        for node_id, cpu in nodes:
            if cpu >= cpu_req:
                new_cpu = cpu - cpu_req
                cursor.execute("UPDATE nodes SET cpu = ? WHERE node_id = ?", (new_cpu, node_id))
                cursor.execute("UPDATE pods SET node_id = ?, status = 'running' WHERE pod_id = ?", (node_id, pod_id))
                conn.commit()
                return node_id
        return None

@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.json
    node_id, cpu = data['node_id'], data['cpu']
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO nodes VALUES (?, ?, ?)", (node_id, cpu, time.time()))
        conn.commit()
    return jsonify({'message': f'Node {node_id} added'})

@app.route('/launch_pod', methods=['POST'])
def launch_pod():
    data = request.json
    pod_id, cpu_req = data['pod_id'], data['cpu']
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pods (pod_id, cpu, node_id, status) VALUES (?, ?, NULL, 'pending')", (pod_id, cpu_req))
        conn.commit()
    assigned_node = schedule_pod(pod_id, cpu_req)
    if assigned_node:
        return jsonify({'message': f'Pod {pod_id} launched on Node {assigned_node}'})
    return jsonify({'error': 'No available nodes, retrying in next cycle'}), 400

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    node_id = data['node_id']
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE nodes SET last_heartbeat = ? WHERE node_id = ?", (time.time(), node_id))
        conn.commit()
    return jsonify({'message': 'Heartbeat received'})

@app.route('/list_nodes', methods=['GET'])
def list_nodes():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT node_id, cpu, last_heartbeat FROM nodes")
        node_list = cursor.fetchall()
    return jsonify([{ 'node_id': node_id, 'cpu': cpu, 'last_heartbeat': last_heartbeat} for node_id, cpu, last_heartbeat in node_list])

@app.route('/pod_usage', methods=['GET'])
def pod_usage():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pod_id, cpu, node_id, status FROM pods")
        pod_list = cursor.fetchall()
    return jsonify([{ 'pod_id': pod_id, 'cpu': cpu, 'node_id': node_id, 'status': status} for pod_id, cpu, node_id, status in pod_list])

def heartbeat_checker():
    while True:
        time.sleep(10)
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT node_id FROM nodes WHERE ? - last_heartbeat > 30", (time.time(),))
            failed_nodes = cursor.fetchall()
            for (node_id,) in failed_nodes:
                logging.warning(f"Node {node_id} failed!")
                cursor.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))
                cursor.execute("UPDATE pods SET node_id = NULL, status = 'pending' WHERE node_id = ?", (node_id,))
            conn.commit()

def auto_heartbeat():
    while True:
        time.sleep(5)
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE nodes SET last_heartbeat = ?", (time.time(),))
            conn.commit()

threading.Thread(target=heartbeat_checker, daemon=True).start()
threading.Thread(target=auto_heartbeat, daemon=True).start()
threading.Thread(target=auto_reschedule, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
