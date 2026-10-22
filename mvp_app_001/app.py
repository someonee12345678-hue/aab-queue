"""AAB Pocket Task Board v0.1 (AAB-MVP-APP-001). Python 3.10+ standard library only.

Run: python3 app.py [--port 8765] [--db goals.json]   (binds 127.0.0.1 only)
"""
import argparse
import json
import os
import re
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STATUSES = ("TODO", "DOING", "DONE")
MAX_TITLE = 120
HOST = "127.0.0.1"


class GoalStore:
    """JSON-file goal store. Fail-closed on corrupt data; atomic replace writes."""

    def __init__(self, path):
        self.path = Path(path)

    def _load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("goal store is unreadable or corrupt: %s" % exc) from None
        goals = data.get("goals") if isinstance(data, dict) else None
        if not isinstance(goals, list):
            raise ValueError("goal store has invalid structure")
        seen = set()
        for g in goals:
            if (not isinstance(g, dict) or set(g) != {"id", "title", "status"}
                    or type(g["id"]) is not int or g["id"] < 1 or g["id"] in seen
                    or not isinstance(g["title"], str) or g["status"] not in STATUSES):
                raise ValueError("goal store contains an invalid goal record")
            seen.add(g["id"])
        return goals

    def _save(self, goals):
        directory = self.path.parent if str(self.path.parent) else Path(".")
        directory.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".goals-", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump({"goals": goals}, fh, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def list_goals(self):
        return [dict(g) for g in self._load()]

    def add_goal(self, title):
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        if len(title) > MAX_TITLE:
            raise ValueError("title must be at most %d characters" % MAX_TITLE)
        goals = self._load()
        goal = {"id": max((g["id"] for g in goals), default=0) + 1,
                "title": title, "status": "TODO"}
        goals.append(goal)
        self._save(goals)
        return dict(goal)

    def set_status(self, goal_id, status):
        if type(goal_id) is not int:
            raise TypeError("goal id must be an integer")
        if not isinstance(status, str):
            raise TypeError("status must be a string")
        if status not in STATUSES:
            raise ValueError("status must be one of TODO, DOING, DONE")
        goals = self._load()
        for g in goals:
            if g["id"] == goal_id:
                g["status"] = status
                self._save(goals)
                return dict(g)
        raise KeyError(goal_id)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AAB Pocket Task Board</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--fg:#e2e8f0;--mut:#94a3b8;--acc:#38bdf8;--todo:#f59e0b;--doing:#a78bfa;--done:#34d399}
*{box-sizing:border-box}body{margin:0;font:16px/1.4 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{padding:16px;position:sticky;top:0;background:var(--bg);border-bottom:1px solid #334155}
h1{margin:0 0 4px;font-size:1.3rem}main{padding:12px;max-width:640px;margin:auto}
form{display:flex;gap:8px;margin-bottom:12px}label.sr{position:absolute;left:-9999px}
input{flex:1;min-height:48px;padding:10px;font-size:1rem;border-radius:10px;border:1px solid #475569;background:#0b1220;color:var(--fg)}
button{min-height:48px;min-width:48px;padding:10px 14px;font-size:1rem;border:0;border-radius:10px;background:var(--acc);color:#04263a;font-weight:600}
.bar{display:flex;gap:8px;margin-bottom:12px}.bar button{flex:1;background:#334155;color:var(--fg)}
ul{list-style:none;padding:0;margin:0}li{background:var(--card);border-radius:12px;padding:12px;margin-bottom:10px}
.t{word-break:break-word;margin-bottom:8px}.row{display:flex;gap:6px}.row button{flex:1;background:#334155;color:var(--fg)}
.row button[aria-pressed=true].TODO{background:var(--todo);color:#000}.row button[aria-pressed=true].DOING{background:var(--doing);color:#000}
.row button[aria-pressed=true].DONE{background:var(--done);color:#000}#msg{color:var(--mut);min-height:1.4em}
</style></head><body>
<header><h1>AAB Pocket Task Board</h1><div id="msg" role="status" aria-live="polite"></div></header>
<main>
<form id="f"><label class="sr" for="title">New goal title</label>
<input id="title" maxlength="120" placeholder="New goal, e.g. Build app" required>
<button type="submit">Add</button></form>
<div class="bar"><button id="refresh" type="button">Refresh</button>
<button id="export" type="button">Export JSON</button></div>
<ul id="list" aria-label="Goals"></ul></main>
<script>
const API="/api/goals";const list=document.getElementById("list"),msg=document.getElementById("msg");
function say(t){msg.textContent=t}
async function call(url,opt){const r=await fetch(url,opt);const b=await r.json().catch(()=>({}));if(!r.ok)throw new Error(b.error||("HTTP "+r.status));return b}
function render(goals){list.replaceChildren();if(!goals.length){const li=document.createElement("li");li.textContent="No goals yet.";list.append(li)}
for(const g of goals){const li=document.createElement("li");const t=document.createElement("div");t.className="t";t.textContent="#"+g.id+" "+g.title;
const row=document.createElement("div");row.className="row";row.setAttribute("role","group");row.setAttribute("aria-label","Status for goal "+g.id);
for(const s of ["TODO","DOING","DONE"]){const b=document.createElement("button");b.type="button";b.className=s;b.textContent=s;
b.setAttribute("aria-pressed",String(g.status===s));b.onclick=()=>setStatus(g.id,s);row.append(b)}
li.append(t,row);list.append(li)}}
async function load(){try{render(await call(API));say("Loaded")}catch(e){say("Error: "+e.message)}}
async function setStatus(id,s){try{await call(API+"/"+id,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:s})});await load();say("Goal "+id+" is "+s)}catch(e){say("Error: "+e.message)}}
document.getElementById("f").onsubmit=async ev=>{ev.preventDefault();const i=document.getElementById("title");
try{await call(API,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title:i.value})});i.value="";await load();say("Added")}catch(e){say("Error: "+e.message)}};
document.getElementById("refresh").onclick=load;document.getElementById("export").onclick=()=>{location.href="/api/export"};
load();
</script></body></html>
"""

GOAL_PATH = re.compile(r"^/api/goals/([1-9][0-9]{0,17})$")
MAX_BODY = 16384


class Handler(BaseHTTPRequestHandler):
    server_version = "AABPocketBoard/0.1"
    store = None  # set by make_server

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _err(self, code, text):
        self._send(code, {"error": text})

    def _json_body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            raise ValueError("bad Content-Length")
        if length <= 0 or length > MAX_BODY:
            raise ValueError("missing or oversized body")
        obj = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("body must be a JSON object")
        return obj

    def _store_call(self, fn, *args):
        try:
            return fn(*args), None
        except KeyError:
            return None, (404, "goal not found")
        except (ValueError, TypeError) as exc:
            if "store" in str(exc):
                return None, (503, "goal store unreadable; not modified")
            return None, (400, str(exc))

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            return self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        if path in ("/api/goals", "/api/export"):
            goals, err = self._store_call(self.store.list_goals)
            if err:
                return self._err(*err)
            if path == "/api/goals":
                return self._send(200, goals)
            return self._send(200, {"app": "AAB Pocket Task Board", "version": "0.1",
                                    "goals": goals},
                              extra={"Content-Disposition":
                                     'attachment; filename="pocket-task-board-export.json"'})
        self._err(404, "not found")

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/goals":
            return self._err(404, "not found")
        try:
            obj = self._json_body()
        except (ValueError, UnicodeDecodeError):
            return self._err(400, "invalid JSON body")
        if set(obj) != {"title"}:
            return self._err(400, "body must be {\"title\": string}")
        goal, err = self._store_call(self.store.add_goal, obj["title"])
        if err:
            return self._err(*err)
        self._send(201, goal)

    def do_PATCH(self):
        m = GOAL_PATH.match(self.path.split("?", 1)[0])
        if not m:
            return self._err(404, "not found")
        try:
            obj = self._json_body()
        except (ValueError, UnicodeDecodeError):
            return self._err(400, "invalid JSON body")
        if set(obj) != {"status"}:
            return self._err(400, "body must be {\"status\": \"TODO\"|\"DOING\"|\"DONE\"}")
        goal, err = self._store_call(self.store.set_status, int(m.group(1)), obj["status"])
        if err:
            return self._err(*err)
        self._send(200, goal)

    def do_PUT(self):
        self._err(404, "not found")

    do_DELETE = do_PUT


def make_server(db_path, port=0):
    """Return an HTTPServer bound only to 127.0.0.1 serving the board for db_path."""
    handler = type("BoundHandler", (Handler,), {"store": GoalStore(db_path)})
    return HTTPServer((HOST, port), handler)


def main(argv=None):
    p = argparse.ArgumentParser(description="AAB Pocket Task Board v0.1 (loopback only)")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--db", default="goals.json")
    args = p.parse_args(argv)
    server = make_server(args.db, args.port)
    print("http://%s:%d" % (HOST, server.server_port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
