"""
auth.py
-------
Authentication and session management module.
Provides secure password hashing, timing-attack-safe comparison,
and role-based access control (RBAC) helpers.
"""

import hashlib
import hmac
import streamlit as st
from typing import Optional, Dict, Any, Tuple
from database import get_user_by_username


def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain password against the stored hash in constant time."""
    if not plain_password or not stored_hash:
        return False
    computed_hash = hash_password(plain_password)
    return hmac.compare_digest(computed_hash, stored_hash)


def init_session() -> None:
    """Initializes Streamlit session state keys if not already set."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "last_login" not in st.session_state:
        st.session_state.last_login = None
    if "flash_notification" not in st.session_state:
        st.session_state.flash_notification = None


def authenticate(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Authenticates a user by username and password.
    Returns (success, user_dict, message).
    """
    if not username.strip() or not password:
        return False, None, "Please provide both username and password."

    user = get_user_by_username(username.strip())
    if not user:
        return False, None, "Invalid username or password."

    if not user.get("active", True):
        return False, None, "This account is inactive. Please contact your manager."

    if verify_password(password, user.get("password_hash", "")):
        # Strip sensitive credentials before keeping in session
        safe_user = {
            "id": user.get("id"),
            "username": user.get("username"),
            "display_name": user.get("display_name"),
            "role": user.get("role"),
            "department": user.get("department", "General"),
            "default_project_id": user.get("default_project_id", "PRJ-101")
        }
        return True, safe_user, "Sign in successful."

    return False, None, "Invalid username or password."


def login_user(user_data: Dict[str, Any]) -> None:
    st.session_state.user = user_data


def logout_user() -> None:
    st.session_state.user = None


def get_current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("user")


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def has_role(role: str) -> bool:
    user = get_current_user()
    if not user:
        return False
    return user.get("role") == role
