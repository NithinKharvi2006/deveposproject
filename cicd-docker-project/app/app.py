"""
Task Manager API
A simple Flask REST API used as the demo application for the
CI/CD Pipeline with GitHub Actions & Docker project.

Endpoints:
    GET    /health          -> service health check (used by Docker/K8s probes)
    GET    /tasks            -> list all tasks
    POST   /tasks            -> create a new task
    GET    /tasks/<id>       -> get a single task
    PUT    /tasks/<id>       -> update a task
    DELETE /tasks/<id>       -> delete a task
"""

from flask import Flask, jsonify, request
from itertools import count
import os

app = Flask(__name__)

# In-memory "database" - good enough for a demo / CI pipeline project
TASKS = {}
_id_counter = count(1)


def _seed_data():
    for title in ["Set up CI pipeline", "Write Dockerfile", "Deploy to Minikube"]:
        tid = next(_id_counter)
        TASKS[tid] = {"id": tid, "title": title, "done": False}


_seed_data()


@app.get("/health")
def health():
    """Used by Docker HEALTHCHECK / Kubernetes liveness probe."""
    return jsonify(status="ok"), 200


@app.get("/tasks")
def get_tasks():
    return jsonify(list(TASKS.values())), 200


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify(error="title is required"), 400

    tid = next(_id_counter)
    task = {"id": tid, "title": title, "done": bool(data.get("done", False))}
    TASKS[tid] = task
    return jsonify(task), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify(error="task not found"), 404
    return jsonify(task), 200


@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify(error="task not found"), 404

    data = request.get_json(silent=True) or {}
    task["title"] = data.get("title", task["title"])
    task["done"] = data.get("done", task["done"])
    return jsonify(task), 200


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    if task_id not in TASKS:
        return jsonify(error="task not found"), 404
    del TASKS[task_id]
    return jsonify(message="deleted"), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
