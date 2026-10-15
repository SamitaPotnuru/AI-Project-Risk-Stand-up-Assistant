"""
database.py
-----------
Persistent JSON storage layer for AI Project Risk & Stand-up Assistant.
Handles atomic writes, schema validation, safe defaults, and CRUD operations.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = Path(__file__).parent / "db.json"
BACKUP_PATH = Path(__file__).parent / "db.backup.json"

DEFAULT_SCHEMA: Dict[str, Any] = {
    "users": [
        {
            "id": "USR-001",
            "username": "employee",
            "display_name": "Demo Employee",
            "role": "employee",
            "password_hash": "b4bd29480ab196faa782e0d4ecd10c2f4212814105227e5f7992f5bf4b212a64",
            "active": True,
            "department": "Platform Engineering",
            "default_project_id": "PRJ-101"
        },
        {
            "id": "USR-002",
            "username": "manager",
            "display_name": "Demo Manager",
            "role": "manager",
            "password_hash": "e8392925a98c9c22795d1fc5d0dfee5b9a6943f6b768ec5a2a0c077e5ed119cf",
            "active": True,
            "department": "Engineering Management",
            "default_project_id": "PRJ-101"
        }
    ],
    "projects": [
        {
            "id": "PRJ-101",
            "name": "Payment Gateway & Checkout Revamp",
            "description": "Core payment integration, 3D Secure v2 compliance, and unified checkout.",
            "owner": "Demo Manager",
            "target_date": "2026-11-20"
        },
        {
            "id": "PRJ-102",
            "name": "Customer Analytics & Telemetry",
            "description": "Real-time user engagement funnel and telemetry dashboard pipeline.",
            "owner": "Demo Manager",
            "target_date": "2026-10-30"
        },
        {
            "id": "PRJ-103",
            "name": "Mobile Client Performance",
            "description": "App startup reduction under 1.2s and memory leak mitigations.",
            "owner": "Demo Manager",
            "target_date": "2026-12-15"
        }
    ],
    "updates": []
}


def get_db_path() -> Path:
    return DB_PATH


def load_db() -> Dict[str, Any]:
    """Loads database from JSON file with graceful error handling and auto-recovery."""
    if not DB_PATH.exists():
        save_db(DEFAULT_SCHEMA)
        return DEFAULT_SCHEMA

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure top-level keys exist
            if not isinstance(data, dict):
                raise ValueError("Root element of db.json must be a JSON object.")
            data.setdefault("users", [])
            data.setdefault("projects", [])
            data.setdefault("updates", [])
            return data
    except (json.JSONDecodeError, OSError, ValueError) as err:
        # Fallback to backup if available, else reinitialize schema
        if BACKUP_PATH.exists():
            try:
                with open(BACKUP_PATH, "r", encoding="utf-8") as bf:
                    return json.load(bf)
            except Exception:
                pass
        save_db(DEFAULT_SCHEMA)
        return DEFAULT_SCHEMA


def save_db(data: Dict[str, Any]) -> bool:
    """
    Atomically saves data to db.json using a temporary file and replace strategy.
    Prevents corrupt files during interrupted writes.
    """
    tmp_path = DB_PATH.with_suffix(".tmp")
    try:
        # Keep an active backup of the previous healthy state
        if DB_PATH.exists():
            try:
                shutil.copyfile(DB_PATH, BACKUP_PATH)
            except Exception:
                pass

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, DB_PATH)
        return True
    except Exception as e:
        if tmp_path.exists():
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise IOError(f"Failed to persist database to {DB_PATH}: {e}")


# --- Users CRUD ---

def get_all_users() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("users", [])


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    if not username:
        return None
    users = get_all_users()
    for u in users:
        if u.get("username", "").strip().lower() == username.strip().lower():
            return u
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    users = get_all_users()
    for u in users:
        if u.get("id") == user_id:
            return u
    return None


# --- Projects CRUD ---

def get_all_projects() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("projects", [])


def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
    projects = get_all_projects()
    for p in projects:
        if p.get("id") == project_id:
            return p
    return None


# --- Updates CRUD ---

def get_updates(user_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns list of updates, optionally filtered by user_id or project_id."""
    db = load_db()
    updates = db.get("updates", [])
    if user_id:
        updates = [u for u in updates if u.get("user_id") == user_id or u.get("username") == user_id]
    if project_id:
        updates = [u for u in updates if u.get("project_id") == project_id]
    return updates


def get_update_by_id(update_id: str) -> Optional[Dict[str, Any]]:
    db = load_db()
    for u in db.get("updates", []):
        if u.get("id") == update_id:
            return u
    return None


def add_update(update_record: Dict[str, Any]) -> Dict[str, Any]:
    """Adds a new stand-up update and persists to db.json."""
    db = load_db()
    updates = db.setdefault("updates", [])

    # Generate sequential unique ID if not provided
    if not update_record.get("id"):
        nums = []
        for x in updates:
            raw_id = str(x.get("id", ""))
            if raw_id.startswith("UP-"):
                num_part = raw_id.split("-")[-1]
                if num_part.isdigit():
                    nums.append(int(num_part))
        next_num = max(nums, default=1000) + 1
        update_record["id"] = f"UP-{next_num}"

    now_iso = datetime.now().isoformat(timespec="seconds")
    update_record.setdefault("created_at", now_iso)
    update_record.setdefault("updated_at", now_iso)
    update_record.setdefault("manager_decision", "Pending review")
    update_record.setdefault("manager_comment", "")
    update_record.setdefault("manager_followup_date", "")

    updates.append(update_record)
    save_db(db)
    return update_record


def update_submission(update_id: str, new_fields: Dict[str, Any], acting_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Updates an employee submission. Preserves previous version history for auditability.
    Verifies permission (only the author or a manager can edit).
    """
    db = load_db()
    for update in db.get("updates", []):
        if update.get("id") == update_id:
            # Authorization check
            is_owner = (update.get("username") == acting_user.get("username")) or (update.get("user_id") == acting_user.get("id"))
            is_manager = acting_user.get("role") == "manager"
            if not (is_owner or is_manager):
                raise PermissionError("Unauthorized: You cannot edit another employee's record.")

            # Record audit trail
            history = update.setdefault("history", [])
            history.append({
                "modified_at": datetime.now().isoformat(timespec="seconds"),
                "modified_by": acting_user.get("display_name", acting_user.get("username")),
                "previous_status": update.get("status"),
                "previous_progress": update.get("progress"),
                "previous_task": update.get("task")
            })

            # Apply permitted updates
            for key, val in new_fields.items():
                if key not in ("id", "created_at", "user_id", "username"):
                    update[key] = val

            update["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_db(db)
            return update
    return None


def record_manager_action(update_id: str, decision: str, comment: str, followup_date: str = "") -> Optional[Dict[str, Any]]:
    """Records a manager review decision and comment for an update."""
    db = load_db()
    for update in db.get("updates", []):
        if update.get("id") == update_id:
            update["manager_decision"] = decision
            update["manager_comment"] = comment.strip()
            update["manager_followup_date"] = followup_date.strip()
            update["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
            save_db(db)
            return update
    return None
