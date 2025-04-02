# KubernetesKubesim
Run The Main File :- python3 distributedsystems.py 
Add node info with CLI.PY :-  python3 cli.py --add-node node2 5 
Launch node with CLI.PY :-  python3 cli.py --launch-pod pod1 2
List nodes with CLI.PY :-  python3 cli.py --list.nodes 

List nodes with curl :- curl -X GET http://127.0.0.1:5001/list_nodes
Add nodes with curl:- curl -X POST http://127.0.0.1:5001/add_node -H "Content-Type: application/json" -d '{"node_id": "node1", "cpu": 4}'
Heartbeat with curl:- curl -X POST http://127.0.0.1:5001/heartbeat -H "Content-Type: application/json" -d '{"node_id": "node1"}'
Launch Pod with curl:- curl -X POST http://127.0.0.1:5001/launch_pod -H "Content-Type: application/json" -d '{"pod_id": "pod2", "cpu": 1}'


