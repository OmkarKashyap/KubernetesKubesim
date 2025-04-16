# KubernetesKubesim
Run The Main File :- python3 distributedsystems.py 

List Nodes 



List nodes with CLI.PY :-  python3 cli.py --list-nodes
 
List nodes with curl :- curl -X GET http://127.0.0.1:5001/get_nodes



Add Nodes



Add node info with CLI.PY :-  python3 cli.py --add-node node1 6
Add nodes with curl:- curl -X POST http://127.0.0.1:5001/add_node -H "Content-Type: application/json" -d '{"node_id": "node1", "cpu": 4}'



Send Heartbeat (To Prevent Failure)

Heartbeat with curl:- curl -X POST http://127.0.0.1:5001/heartbeat -H "Content-Type: application/json" -d '{"node_id": "node1"}'

You can simulate automatic heartbeats externally using a simple watch or loop script:

while true; do curl -X POST http://127.0.0.1:5001/heartbeat -H "Content-Type: application/json" -d '{"node_id":"node1"}'; sleep 5; done


Launch Pods


Launch node with CLI.PY :-  python3 cli.py --launch-pod pod1 2
Launch Pod with curl:- curl -X POST http://127.0.0.1:5001/launch_pod -H "Content-Type: application/json" -d '{"pod_id": "pod2", "cpu": 1}'




List Pods

python3 cli.py --list-pods

curl http://127.0.0.1:5001/pod_usage



Detect Failed Nodes:

sqlite3 cluster.db "SELECT node_id, last_heartbeat FROM nodes WHERE ? - last_heartbeat > 30"

Flag Node as Failed:


sqlite3 cluster.db "UPDATE nodes SET status = 'failed' WHERE node_id IN (SELECT node_id FROM nodes WHERE ? - last_heartbeat > 30)"

Find Unhealthy Pods on Failed Node:

sqlite3 cluster.db "SELECT pod_id FROM pods WHERE node_id = 'failed_node_id' AND status = 'unhealthy'"

Reschedule Pods to Healthy Nodes:

sqlite3 cluster.db "UPDATE pods SET node_id = 1, status = 'healthy' WHERE pod_id = 2"

Log Actions

echo "Node failed: 'failed_node_id' at $(date)" >> recovery.log
echo "Pod 'pod_id' rescheduled to 'healthy_node_id' at $(date)" >> recovery.log










