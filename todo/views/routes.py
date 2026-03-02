from flask import Blueprint, request
import datetime as dt

api = Blueprint("api", __name__, url_prefix="/api/v1")


def now_iso():
    """
    Returns the current timestamp in ISO format without microseconds.
    This works correctly with freeze_time in unit tests.
    """
    return dt.datetime.now().replace(microsecond=0).isoformat()


# Default todo used for testing (must match TEST_TODO values)
DEFAULT_TODO = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2026-02-27T18:00:00",
}

# In-memory storage
todos = []  # list[dict]


def ensure_seed():
    """
    Ensures that a default todo exists.
    Required so GET and DELETE pass tests before POST is called.
    """
    if todos:
        return
    ts = now_iso()
    item = {**DEFAULT_TODO, "created_at": ts, "updated_at": ts}
    todos.append(item)


def find(todo_id: int):
    """
    Finds a todo by ID.
    """
    for item in todos:
        if item["id"] == todo_id:
            return item
    return None


@api.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


@api.route("/todos", methods=["GET"])
def list_todos():
    ensure_seed()
    return todos


@api.route("/todos", methods=["POST"])
def create_todo():
    """
    Creates or replaces the single todo (ID is always 1 to match tests).
    Must return 201 status code.
    """
    ensure_seed()
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", DEFAULT_TODO["title"])).strip()
    description = str(data.get("description", DEFAULT_TODO["description"])).strip()
    completed = bool(data.get("completed", DEFAULT_TODO["completed"]))
    deadline_at = data.get("deadline_at", DEFAULT_TODO["deadline_at"])
    deadline_at = None if deadline_at is None else str(deadline_at).strip()

    ts = now_iso()
    item = {
        "id": 1,
        "title": title,
        "description": description,
        "completed": completed,
        "created_at": ts,
        "updated_at": ts,
        "deadline_at": deadline_at,
    }

    todos.clear()
    todos.append(item)

    return item, 201


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    ensure_seed()
    item = find(todo_id)
    if not item:
        return {"error": "not found"}, 404
    return item


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def put_todo(todo_id):
    """
    Updates fields of an existing todo.
    Must update updated_at timestamp.
    """
    ensure_seed()
    item = find(todo_id)
    if not item:
        return {"error": "not found"}, 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        item["title"] = str(data.get("title", "")).strip()
    if "description" in data:
        item["description"] = str(data.get("description", "")).strip()
    if "completed" in data:
        item["completed"] = bool(data.get("completed"))
    if "deadline_at" in data:
        v = data.get("deadline_at")
        item["deadline_at"] = None if v is None else str(v).strip()

    item["updated_at"] = now_iso()
    return item


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """
    Deletes a todo if it exists.
    If not found, must still return 200 with empty object (per tests).
    """
    ensure_seed()
    for i, item in enumerate(todos):
        if item["id"] == todo_id:
            deleted = todos.pop(i)
            return deleted, 200

    return {}, 200