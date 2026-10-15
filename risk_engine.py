"""
risk_engine.py
--------------
Rule-based project risk evaluation engine.
Analyzes task updates, blockers, timeline progress, dependencies, and recency.
Provides clear risk levels (High, Medium, Low), categorical labels,
supporting evidence from the task, and suggested next actions.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Tuple
import pandas as pd


# Configurable risk thresholds
DEFAULT_CONFIG = {
    "stale_days_threshold": 3,
    "due_soon_days_threshold": 2,
    "low_progress_threshold": 50,
}


def parse_date(date_val: Any) -> Tuple[bool, Any]:
    """Helper to safely parse dates."""
    if not date_val:
        return False, None
    try:
        if isinstance(date_val, (date, datetime)):
            return True, date_val.date() if isinstance(date_val, datetime) else date_val
        parsed = pd.to_datetime(str(date_val).strip()).date()
        return True, parsed
    except Exception:
        return False, None


def evaluate_task_risk(task: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Evaluates risk for an individual project update record.
    Returns:
        dict: {
            "risk_level": "High" | "Medium" | "Low",
            "category": str,
            "reason": str,
            "evidence": str,
            "suggested_action": str
        }
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}

    status = str(task.get("status", "")).strip().lower()
    blocker = str(task.get("blocker", "")).strip().lower()
    blocker_desc = str(task.get("blocker_desc", "")).strip()
    progress = task.get("progress", 0)
    try:
        progress_val = int(progress)
    except (ValueError, TypeError):
        progress_val = 0

    progress_notes = str(task.get("progress", "") if isinstance(task.get("progress"), str) else task.get("description", "")).strip()
    dependency = str(task.get("dependency", "")).strip()
    due_raw = task.get("due_date", "")
    created_raw = task.get("created_at", "")
    updated_raw = task.get("updated_at", created_raw)
    today = date.today()

    # Rule 1: Explicit Blocker or Blocked Status -> High Risk
    if blocker in ("yes", "true", "1") or status == "blocked":
        evidence_text = blocker_desc or "Explicit blocker indicated with no additional detail provided."
        if dependency:
            evidence_text += f" Related dependency: '{dependency}'."
        return {
            "risk_level": "High",
            "category": "Active Blocker",
            "reason": "An active blocker is impeding delivery progress.",
            "evidence": evidence_text,
            "suggested_action": "Manager to intervene immediately and coordinate with unblocking stakeholders."
        }

    # Rule 2: Incomplete Task with Past Due Date -> High Risk
    has_due, due_date_obj = parse_date(due_raw)
    if has_due and due_date_obj and status != "completed":
        if due_date_obj < today:
            days_overdue = (today - due_date_obj).days
            return {
                "risk_level": "High",
                "category": "Overdue Schedule",
                "reason": f"Target due date passed {days_overdue} day(s) ago; task remains incomplete.",
                "evidence": f"Due date was {due_date_obj.strftime('%Y-%m-%d')} ({days_overdue} days overdue). Current status is '{task.get('status')}'.",
                "suggested_action": "Re-baseline the milestone target date or reduce feature scope to unblock release."
            }

    # Rule 3: Missing Information / Incomplete Update -> Medium Risk
    if status in ("unknown", "") or (not progress_notes and progress_val == 0):
        return {
            "risk_level": "Medium",
            "category": "Missing Information",
            "reason": "The update contains insufficient detail to confirm delivery trajectory.",
            "evidence": "Status is undefined or progress notes are absent.",
            "suggested_action": "Request a clarified stand-up update with concrete progress metrics."
        }

    # Rule 4: Approaching Due Date with Low Progress -> Medium Risk
    if has_due and due_date_obj and status != "completed":
        days_until_due = (due_date_obj - today).days
        if 0 <= days_until_due <= cfg["due_soon_days_threshold"] and progress_val < cfg["low_progress_threshold"]:
            return {
                "risk_level": "Medium",
                "category": "At-Risk Velocity",
                "reason": f"Due in {days_until_due} day(s) but progress is only {progress_val}%.",
                "evidence": f"Due date is {due_date_obj.strftime('%Y-%m-%d')} with {progress_val}% completed.",
                "suggested_action": "Assign peer support or pair programming to accelerate completion."
            }

    # Rule 5: Unresolved External Dependency -> Medium Risk
    if dependency and dependency.lower() not in ("none", "n/a", "no", "nil") and status != "completed":
        return {
            "risk_level": "Medium",
            "category": "Dependency Bottleneck",
            "reason": "Task depends on external teams or third-party assets.",
            "evidence": f"Active external dependency recorded: '{dependency}'.",
            "suggested_action": "Confirm delivery SLA and ETA with the external dependency team."
        }

    # Rule 6: Stale Update (No check-in for N days) -> Medium Risk
    has_updated, updated_date_obj = parse_date(updated_raw)
    if has_updated and updated_date_obj and status != "completed":
        days_stale = (today - updated_date_obj).days
        if days_stale >= cfg["stale_days_threshold"]:
            return {
                "risk_level": "Medium",
                "category": "Stale Update",
                "reason": f"No status check-in recorded for {days_stale} days.",
                "evidence": f"Last recorded check-in was {updated_date_obj.strftime('%Y-%m-%d')} ({days_stale} days ago).",
                "suggested_action": "Prompt the assignee for an updated progress report."
            }

    # Rule 7: Completed or On Track -> Low Risk
    if status == "completed":
        return {
            "risk_level": "Low",
            "category": "Completed",
            "reason": "Task has been marked 100% completed.",
            "evidence": "Status is Completed.",
            "suggested_action": "Verify testing acceptance and transition task to release notes."
        }

    return {
        "risk_level": "Low",
        "category": "On Track",
        "reason": "Task is progressing normally with no rule-based blockers or overdue flags.",
        "evidence": f"Status: {task.get('status', 'In Progress')}, Progress: {progress_val}%, Due: {due_raw or 'No due date'}.",
        "suggested_action": "Continue monitoring regular stand-up check-ins."
    }


def compute_metrics(updates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates overall team risk and status metrics from updates list."""
    total = len(updates)
    if total == 0:
        return {
            "total_updates": 0,
            "completed": 0,
            "blocked": 0,
            "overdue": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "pending_reviews": 0
        }

    completed = 0
    blocked = 0
    overdue = 0
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    pending_reviews = 0

    today = date.today()

    for u in updates:
        status = str(u.get("status", "")).lower()
        blocker = str(u.get("blocker", "")).lower()

        if status == "completed":
            completed += 1
        if blocker in ("yes", "true", "1") or status == "blocked":
            blocked += 1

        has_due, due_obj = parse_date(u.get("due_date"))
        if has_due and due_obj and status != "completed" and due_obj < today:
            overdue += 1

        if u.get("manager_decision", "Pending review") == "Pending review":
            pending_reviews += 1

        risk = evaluate_task_risk(u)
        level = risk["risk_level"]
        if level == "High":
            high_risk += 1
        elif level == "Medium":
            medium_risk += 1
        else:
            low_risk += 1

    return {
        "total_updates": total,
        "completed": completed,
        "blocked": blocked,
        "overdue": overdue,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "pending_reviews": pending_reviews
    }
