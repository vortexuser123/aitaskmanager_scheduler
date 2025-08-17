from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json, os, threading

FILE = "tasks.json"
app = Flask(__name__)
lock = threading.Lock()
sched = BackgroundScheduler(); sched.start()

def load():
    if not os.path.exists(FILE): return []
    with open(FILE,"r") as f: return json.load(f)

def save(tasks):
    with lock:
        with open(FILE,"w") as f: json.dump(tasks,f,indent=2)

def remind(task):
    print(f"[REMINDER] {task['title']} @ {task['due']} -> {task.get('note','')}")

@app.route("/tasks", methods=["GET","POST"])
def tasks():
    if request.method == "GET": return jsonify(load())
    t = request.json; tasks = load(); tasks.append(t); save(tasks)
    if "due" in t:
        run_at = datetime.fromisoformat(t["due"])
        sched.add_job(remind, 'date', run_date=run_at, args=[t])
    return jsonify({"ok":True})

@app.route("/tasks/<int:i>", methods=["DELETE"])
def delete(i):
    tasks = load(); 
    if 0<=i<len(tasks): tasks.pop(i); save(tasks); return {"ok":True}
    return {"error":"not found"},404

if __name__ == "__main__":
    app.run(port=5050)
