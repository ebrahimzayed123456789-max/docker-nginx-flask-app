
from flask import Flask, jsonify, request, render_template_string
import os, datetime, json
import psycopg2
import redis as redis_lib

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        database=os.environ.get("POSTGRES_DB", "taskmanager"),
        user=os.environ.get("POSTGRES_USER", "appuser"),
        password=os.environ.get("POSTGRES_PASSWORD", "secret"),
        connect_timeout=5,
    )

def get_redis():
    return redis_lib.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=6379, decode_responses=True, socket_timeout=3,
    )

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>✅ Task Manager</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <div class="container">
    <h1>✅ Task Manager</h1>
    <div class="info-grid">
      <div class="info-card"><div class="label">Worker</div><div class="value">{{ worker }}</div></div>
      <div class="info-card"><div class="label">DB</div><div class="value {{ 'ok' if db_ok else 'err' }}">{{ 'Connected' if db_ok else 'Error' }}</div></div>
      <div class="info-card"><div class="label">Redis</div><div class="value {{ 'ok' if redis_ok else 'err' }}">{{ 'Connected' if redis_ok else 'Error' }}</div></div>
      <div class="info-card"><div class="label">Time</div><div class="value">{{ time }}</div></div>
    </div>
    <div class="endpoints">
      <h2>API Endpoints</h2>
      <a href="/api/tasks" class="btn">GET /api/tasks</a>
      <a href="/api/health" class="btn green">GET /api/health</a>
    </div>
    <div class="add-form">
      <h2>Add Task</h2>
      <input id="title" placeholder="Task title" type="text">
      <input id="priority" placeholder="Priority: low / medium / high" type="text" value="medium">
      <button onclick="addTask()">Add Task</button>
      <div id="msg"></div>
    </div>
  </div>
  <script>
    async function addTask() {
      const title = document.getElementById('title').value;
      const priority = document.getElementById('priority').value;
      const r = await fetch('/api/tasks', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({title, priority})
      });
      const d = await r.json();
      document.getElementById('msg').textContent = d.message || d.error;
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    db_ok, redis_ok = False, False
    try: db=get_db(); db.close(); db_ok=True
    except: pass
    try: r=get_redis(); r.ping(); redis_ok=True
    except: pass
    return render_template_string(HTML,
        worker=os.environ.get("SERVER_NAME","flask"),
        time=datetime.datetime.now().strftime("%H:%M:%S"),
        db_ok=db_ok, redis_ok=redis_ok)

@app.route("/api/health")
def health():
    db_ok, redis_ok = False, False
    try: db=get_db(); db.close(); db_ok=True
    except: pass
    try: r=get_redis(); r.ping(); redis_ok=True
    except: pass
    status = "healthy" if (db_ok and redis_ok) else "degraded"
    return jsonify({"status":status,"worker":os.environ.get("SERVER_NAME","flask"),
                    "db":db_ok,"redis":redis_ok,"time":str(datetime.datetime.now())}), 200 if status=="healthy" else 503

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        r = get_redis()
        cached = r.get("tasks:all")
        if cached:
            return jsonify({"tasks":json.loads(cached), "source":"cache"})
    except: pass
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("SELECT id, title, priority, done, created_at FROM tasks ORDER BY id DESC LIMIT 100")
        tasks = [{"id":row[0],"title":row[1],"priority":row[2],"done":row[3],"created_at":str(row[4])} for row in cur.fetchall()]
        cur.close(); db.close()
        try: get_redis().setex("tasks:all", 30, json.dumps(tasks))
        except: pass
        return jsonify({"tasks":tasks, "source":"database"})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title","").strip()
    priority = data.get("priority","medium").strip()
    if not title:
        return jsonify({"error":"title required"}), 400
    if priority not in ("low","medium","high"):
        priority = "medium"
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO tasks (title, priority) VALUES (%s, %s) RETURNING id", (title, priority))
        task_id = cur.fetchone()[0]; db.commit(); cur.close(); db.close()
        try: get_redis().delete("tasks:all")
        except: pass
        return jsonify({"message":"Task added!", "id":task_id}), 201
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@app.route("/api/tasks/<int:task_id>/done", methods=["PATCH"])
def complete_task(task_id):
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("UPDATE tasks SET done=true WHERE id=%s RETURNING id", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error":"Task not found"}), 404
        db.commit(); cur.close(); db.close()
        try: get_redis().delete("tasks:all")
        except: pass
        return jsonify({"message":f"Task {task_id} marked done"})
    except Exception as e:
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
