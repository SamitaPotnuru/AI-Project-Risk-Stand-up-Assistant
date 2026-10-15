"""
app.py
------
AI Project Risk & Stand-up Assistant
Enterprise Role-Based Employee and Manager Dashboard.
Built with Python, Streamlit, Pandas, Plotly, and persistent JSON database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Core modules
from database import (
    load_db, get_all_projects, get_project_by_id,
    get_updates, add_update, update_submission, record_manager_action,
    get_user_by_username
)
from auth import (
    init_session, authenticate, login_user, logout_user,
    get_current_user, is_authenticated, has_role
)
from risk_engine import evaluate_task_risk, compute_metrics, parse_date
from ai_assistant import query_ai_assistant, build_executive_report_ui

# Page Configuration
st.set_page_config(
    page_title="NxtWave Project Operations | AI Risk & Stand-up Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Comprehensive Enterprise Design System & Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    html, body, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* Guarantee Streamlit Material Symbols Icon Rendering */
    [data-testid="stIconMaterial"], 
    span[data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* Background and Layout */
    .stApp {
        background-color: #f8fafc;
    }

    /* Hero Banner for Dashboards */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #0f172a 100%);
        border-radius: 16px;
        padding: 26px 32px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -60px;
        right: -40px;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.35);
        color: #c7d2fe;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Professional KPI Metric Cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 18px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -4px rgba(0, 0, 0, 0.03);
        border-color: #cbd5e1;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em;
    }

    /* Tabs Segmented Navigation */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 10px 22px !important;
        color: #64748b !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4f46e5 !important;
        border-bottom: 2px solid #4f46e5 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    /* Sidebar Header & Collapse / Expand Side Arrow Buttons */
    div[data-testid="stSidebarHeader"] {
        padding: 10px 14px 4px 14px !important;
        background-color: #ffffff !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        height: auto !important;
        min-height: unset !important;
    }
    div[data-testid="stLogoSpacer"] {
        display: none !important;
    }
    div[data-testid="stSidebarCollapseButton"] button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background: #f1f5f9 !important;
        padding: 6px 8px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stSidebarCollapseButton"] button:hover {
        background: #e2e8f0 !important;
        border-color: #94a3b8 !important;
        transform: scale(1.05) !important;
    }
    div[data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-size: 1.35rem !important;
        color: #334155 !important;
        display: inline-block !important;
    }

    /* Floating control when sidebar is collapsed (Expand button) */
    div[data-testid="stSidebarCollapsedControl"] button {
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSidebarCollapsedControl"] button:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
    }
    div[data-testid="stSidebarCollapsedControl"] button [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-size: 1.35rem !important;
        color: #334155 !important;
    }

    div[data-testid="stSidebarUserContent"] {
        padding-top: 0.5rem !important;
        height: 100% !important;
    }

    /* Sidebar Layout - Pin Logout Button to Bottom with Premium UI */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        min-height: calc(100vh - 90px) !important;
    }
    section[data-testid="stSidebar"] div.stButton {
        margin-top: auto !important;
        padding-top: 18px !important;
        border-top: 1px solid #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] div.stButton button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 10px 16px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    section[data-testid="stSidebar"] div.stButton button:hover {
        background: #fff1f2 !important;
        color: #e11d48 !important;
        border-color: #fecdd3 !important;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.12) !important;
        transform: translateY(-1px) !important;
    }
    .user-profile-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 18px;
    }
    .user-avatar-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.28);
    }

    /* Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.32) !important;
    }
    .stButton button[kind="secondary"] {
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
    }

    /* Form Fields */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 8px !important;
        border-color: #e2e8f0 !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
    }

    /* Form Section Dividers */
    .form-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Card Containers */
    .pro-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 22px 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }

    /* Risk Badges */
    .badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 10px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 10px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    /* DataFrame Polish */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }

    /* Executive Briefing Dashboard UI */
    .exec-dashboard {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        margin-top: 14px;
    }
    .exec-header {
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 16px;
        margin-bottom: 18px;
    }
    .exec-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 6px;
    }
    .exec-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.08);
        color: #4f46e5;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
        display: inline-block;
    }
    .exec-meta-chips {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .exec-chip {
        font-size: 0.75rem;
        color: #64748b;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
    }
    .exec-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin-top: 4px;
    }
    .exec-subtitle {
        font-size: 0.88rem;
        color: #64748b;
        margin-top: 2px;
    }

    /* KPI Grid */
    .exec-section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin: 22px 0 12px 0;
    }
    .exec-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
    }
    .kpi-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        transition: transform 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .kpi-card.kpi-danger {
        background: #fff1f2;
        border-color: #fecdd3;
    }
    .kpi-card.kpi-warning {
        background: #fffbeb;
        border-color: #fde68a;
    }
    .kpi-card.kpi-success {
        background: #f0fdf4;
        border-color: #bbf7d0;
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        color: #64748b;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 4px 0 2px 0;
    }
    .kpi-sub {
        font-size: 0.7rem;
        color: #94a3b8;
    }

    /* Alert / Critical Cards */
    .exec-alert-card {
        background: #ffffff;
        border: 1px solid #fecdd3;
        border-left: 4px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.04);
    }
    .exec-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
    }
    .task-pill {
        background: #0f172a;
        color: #ffffff;
        font-family: monospace;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    .task-name {
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
    }
    .badge-category-red {
        background: #fee2e2;
        color: #b91c1c;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .badge-category-amber {
        background: #fef3c7;
        color: #b45309;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .exec-card-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 12px;
    }
    .evidence-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #334155;
        line-height: 1.45;
    }
    .action-box {
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.85rem;
        color: #312e81;
        line-height: 1.45;
    }

    /* Watchlist Rows */
    .watchlist-card {
        background: #fafaf9;
        border: 1px solid #e7e5e4;
        border-left: 3px solid #f59e0b;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .watchlist-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #1c1917;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .watchlist-desc {
        font-size: 0.82rem;
        color: #57534e;
        margin: 4px 0;
    }
    .watchlist-action {
        font-size: 0.8rem;
        color: #4338ca;
        background: #e0e7ff;
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Action Step List */
    .action-step-card {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .step-number-badge {
        background: #4f46e5;
        color: #ffffff;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .step-text {
        font-size: 0.88rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.4;
    }
    .empty-banner-clean {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

init_session()

# ==============================================================================
# AUTHENTICATION DIALOGS & SCREEN
# ==============================================================================

@st.dialog("🌐 Continue with Google")
def show_google_sso_dialog():
    custom_g = st.text_input("Google Workspace Email", placeholder="Enter corporate Google email (e.g. name@company.com)...", label_visibility="collapsed")
    if st.button("Authorize with Google SSO", type="primary", use_container_width=True):
        if custom_g.strip():
            email_clean = custom_g.strip().lower()
            user_part = email_clean.split("@")[0]
            matched_user = get_user_by_username(user_part)
            if matched_user:
                login_user({
                    "id": matched_user.get("id"),
                    "username": matched_user.get("username"),
                    "display_name": matched_user.get("display_name"),
                    "role": matched_user.get("role"),
                    "department": matched_user.get("department", "General"),
                    "default_project_id": matched_user.get("default_project_id", "PRJ-101")
                })
            else:
                login_user({
                    "id": "USR-GOOGLE",
                    "username": user_part,
                    "display_name": user_part.capitalize(),
                    "role": "employee",
                    "department": "Platform Engineering",
                    "default_project_id": "PRJ-101"
                })
            st.toast(f"Authenticated via Google SSO ({email_clean})!", icon="✅")
            st.rerun()
        else:
            st.warning("Please enter your Google Workspace email address.")


if not is_authenticated():
    # Brand Top Nav
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0 20px 0;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; font-weight: bold; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);">🚀</div>
            <div>
                <span style="font-weight: 800; font-size: 1.2rem; color: #0f172a; letter-spacing: -0.02em;">NxtWave Project Operations</span>
                <span style="font-size: 0.72rem; background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 10px; font-weight: 700; margin-left: 8px;">v2.0 PRO</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_hero, col_login = st.columns([1.15, 0.95], gap="large")

    with col_hero:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #0f172a 100%); border-radius: 16px; padding: 34px 38px; color: white; box-shadow: 0 12px 30px -8px rgba(15, 23, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.08); position: relative;">
            <div style="display: inline-block; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(129, 140, 248, 0.4); color: #c7d2fe; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 4px 12px; border-radius: 20px; margin-bottom: 16px;">
                ENTERPRISE PROJECT ASSISTANT
            </div>
            <h1 style="font-size: 2.15rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.2; margin-bottom: 12px; color: #ffffff;">
                Continuous Stand-up Intelligence & Risk Governance
            </h1>
            <p style="color: #cbd5e1; font-size: 1.02rem; line-height: 1.6; margin-bottom: 24px;">
                Eliminate scattered updates across Slack, meetings, and static sheets. Our assistant unifies stand-up tracking, automatically classifies delivery risks with empirical evidence, and synthesizes executive briefings.
            </p>
            <div style="display: grid; grid-template-columns: 1fr; gap: 14px; margin-top: 10px;">
                <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); padding: 12px 16px; border-radius: 10px;">
                    <span style="font-size: 1.25rem;">⚡</span>
                    <div>
                        <div style="font-weight: 700; font-size: 0.94rem; color: #ffffff;">Automated Risk Engine</div>
                        <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 2px;">Rule heuristics detect blockers, overdue deliverables, and dependency choke points.</div>
                    </div>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); padding: 12px 16px; border-radius: 10px;">
                    <span style="font-size: 1.25rem;">🛡️</span>
                    <div>
                        <div style="font-weight: 700; font-size: 0.94rem; color: #ffffff;">Strict Role-Based Isolation</div>
                        <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 2px;">Employees manage isolated check-ins with an audit trail, while managers oversee team telemetry.</div>
                    </div>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); padding: 12px 16px; border-radius: 10px;">
                    <span style="font-size: 1.25rem;">🤖</span>
                    <div>
                        <div style="font-weight: 700; font-size: 0.94rem; color: #ffffff;">Factual Executive Briefings</div>
                        <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 2px;">Offline rule-based synthesis or external LLMs generate board-ready reports with zero hallucination.</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_login:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 28px 32px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);">
            <div style="font-weight: 800; font-size: 1.45rem; color: #0f172a; letter-spacing: -0.02em;">Welcome Back</div>
            <div style="font-size: 0.92rem; color: #64748b; margin-top: 4px; margin-bottom: 20px;">Sign in to access your designated workspace</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. employee or manager")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_login = st.form_submit_button("Sign In to Workspace", type="primary", use_container_width=True)

        if submit_login:
            success, user_data, msg = authenticate(username, password)
            if success:
                login_user(user_data)
                st.toast(f"Welcome back, {user_data.get('display_name')}!", icon="👋")
                st.rerun()
            else:
                st.error(f"⚠️ {msg}")



        # Alternative SSO Divider
        st.markdown("""
        <div style="display: flex; align-items: center; margin: 10px 0 14px 0; color: #94a3b8; font-size: 0.78rem;">
            <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
            <span style="padding: 0 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">or</span>
            <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Continue with Google button
        if st.button("🌐 Continue with Google", use_container_width=True):
            show_google_sso_dialog()

    st.stop()


# ==============================================================================
# LOGGED-IN NAVIGATION & SIDEBAR
# ==============================================================================

current_user = get_current_user()
user_role = current_user.get("role", "employee")

with st.sidebar:
    # Sidebar Brand
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold;">🚀</div>
        <div>
            <div style="font-weight: 800; font-size: 1.05rem; color: #0f172a; line-height: 1.2;">Project Operations</div>
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 500;">AI Risk & Stand-up</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User Profile Card
    display_name = current_user.get("display_name", "User")
    initials = "".join([part[0].upper() for part in display_name.split()[:2]]) or "U"
    role_color = "#3730a3" if user_role == "employee" else "#86198f"
    role_bg = "#e0e7ff" if user_role == "employee" else "#fae8ff"

    st.markdown(f"""
    <div class="sidebar-user-card">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="user-avatar-circle">{initials}</div>
            <div>
                <div style="font-weight: 700; font-size: 0.95rem; color: #0f172a;">{display_name}</div>
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                    <span style="font-size: 0.72rem; background: {role_bg}; color: {role_color}; padding: 2px 8px; border-radius: 10px; font-weight: 700;">{user_role.upper()}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Log Out of Session", type="secondary", use_container_width=True):
        logout_user()
        st.rerun()


# ==============================================================================
# EMPLOYEE DASHBOARD
# ==============================================================================

if user_role == "employee":
    my_updates = get_updates(user_id=current_user.get("id"))
    my_metrics = compute_metrics(my_updates)

    # Hero Banner
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-tag"><span>●</span> EMPLOYEE WORKSPACE</div>
        <div class="hero-title">Welcome back, {current_user.get('display_name')}</div>
        <div class="hero-subtitle">Department: {current_user.get('department')} • User ID: {current_user.get('id')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key Stat Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("My Total Tasks", my_metrics["total_updates"])
    m2.metric("In Progress", sum(1 for u in my_updates if str(u.get("status")).lower() == "in progress"))
    m3.metric("Blockers Reported", my_metrics["blocked"])
    m4.metric("Completed Tasks", my_metrics["completed"])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Flash Toast Notification Display
    if st.session_state.get("flash_notification"):
        notif = st.session_state["flash_notification"]
        st.toast(f"🎉 {notif.get('title', 'Submitted Successfully!')} — Task {notif.get('task_id', '')}", icon="✅")
        st.session_state["flash_notification"] = None

    tab_submit, tab_history = st.tabs(["📝 Submit Daily Stand-up", "📋 My Submission History & Edits"])

    # --- TAB 1: SUBMIT UPDATE ---
    with tab_submit:
        projects = get_all_projects()
        project_options = {p["name"]: p["id"] for p in projects}

        with st.form("employee_submission_form", clear_on_submit=False):
            st.markdown('<div class="form-section-title">📌 1. Project & Task Identity</div>', unsafe_allow_html=True)
            col_p1, col_p2 = st.columns([1.2, 0.8])
            selected_proj_name = col_p1.selectbox("Assigned Project *", list(project_options.keys()))
            task_id = col_p2.text_input("Task ID *", placeholder="e.g. T-105")

            task_name = st.text_input("Task Title *", placeholder="e.g. Integrate Redis Cache for User Sessions")
            task_desc = st.text_area("Detailed Progress & What was completed *", placeholder="Explain progress made, what was delivered, and current work...")

            st.markdown('<div class="form-section-title">⏱️ 2. Execution & Schedule</div>', unsafe_allow_html=True)
            col_s1, col_s2, col_s3 = st.columns(3)
            status = col_s1.selectbox("Task Status *", ["Not Started", "In Progress", "Blocked", "Completed"])
            progress_pct = col_s2.slider("Progress Percentage *", min_value=0, max_value=100, value=25, step=5)
            has_due = col_s3.checkbox("Set Target Due Date", value=True)

            col_d1, col_d2 = st.columns(2)
            start_date_val = col_d1.date_input("Start Date", value=date.today())
            due_date_val = col_d2.date_input("Due Date", value=date.today(), disabled=not has_due)

            st.markdown('<div class="form-section-title">🛡️ 3. Blockers, Dependencies & Next Steps</div>', unsafe_allow_html=True)
            col_b1, col_b2 = st.columns([0.8, 1.2])
            is_blocked = col_b1.selectbox("Is there an active blocker?", ["No", "Yes"], index=1 if status == "Blocked" else 0)
            blocker_desc = col_b2.text_input("Blocker Explanation (Required if blocked)", placeholder="e.g. Awaiting AWS IAM policy approval")

            dependency = st.text_input("External Dependency (if any)", placeholder="e.g. DevOps Team, Third-party Webhook spec")
            next_action = st.text_input("Next Planned Action *", placeholder="e.g. Run integration test suite and push PR")
            comments = st.text_input("Additional Notes or Context", placeholder="Optional remarks...")

            submitted = st.form_submit_button("Submit Daily Update", type="primary", use_container_width=True)

        if submitted:
            # Client & Server-side Validation
            errors = []
            if not task_name.strip():
                errors.append("Task Title is required.")
            if not task_desc.strip():
                errors.append("Progress description is required.")
            if not next_action.strip():
                errors.append("Next Planned Action is required.")
            if is_blocked == "Yes" and not blocker_desc.strip():
                errors.append("Please provide a description of the blocker so your manager can unblock you.")
            if status == "Blocked" and is_blocked == "No":
                errors.append("Status is marked 'Blocked'; please select 'Yes' for active blocker and explain.")
            if status == "Completed" and progress_pct < 100:
                errors.append("Tasks marked as 'Completed' must have 100% progress.")
            if has_due and due_date_val < start_date_val:
                errors.append("Due date cannot be earlier than the start date.")

            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                new_record = {
                    "user_id": current_user.get("id"),
                    "username": current_user.get("username"),
                    "employee": current_user.get("display_name"),
                    "project_id": project_options[selected_proj_name],
                    "project_name": selected_proj_name,
                    "task_id": task_id.strip() or "T-AUTO",
                    "task": task_name.strip(),
                    "description": task_desc.strip(),
                    "status": status,
                    "progress": progress_pct,
                    "blocker": is_blocked,
                    "blocker_desc": blocker_desc.strip() if is_blocked == "Yes" else "",
                    "dependency": dependency.strip(),
                    "start_date": str(start_date_val),
                    "due_date": str(due_date_val) if has_due else "",
                    "next_action": next_action.strip(),
                    "comments": comments.strip()
                }
                saved = add_update(new_record)
                st.session_state.flash_notification = {
                    "title": "Submitted Successfully!",
                    "task_id": saved.get("id"),
                    "task_name": saved.get("task"),
                    "project": saved.get("project_name"),
                    "status": saved.get("status"),
                    "progress": saved.get("progress"),
                    "time": datetime.now().strftime("%I:%M %p")
                }
                st.rerun()

    # --- TAB 2: MY SUBMISSION HISTORY ---
    with tab_history:
        st.subheader("My Update History")

        if not my_updates:
            st.info("No updates submitted yet. Use the tab above to submit your first daily update.")
        else:
            rows = []
            for u in my_updates:
                risk = evaluate_task_risk(u)
                rows.append({
                    "ID": u.get("id"),
                    "Project": u.get("project_name", "N/A"),
                    "Task ID": u.get("task_id"),
                    "Task": u.get("task"),
                    "Status": u.get("status"),
                    "Progress": f"{u.get('progress')}%",
                    "Due Date": u.get("due_date") or "None",
                    "Blocker": u.get("blocker"),
                    "Manager Decision": u.get("manager_decision", "Pending review"),
                    "Manager Comments": u.get("manager_comment") or "No comments yet",
                    "Created At": u.get("created_at")
                })

            df_my = pd.DataFrame(rows).sort_values("Created At", ascending=False)
            st.dataframe(df_my, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Edit an Active Submission")
            editable_options = {f"{u['id']} | {u['task']} ({u['status']})": u['id'] for u in my_updates if u.get("status") != "Completed"}

            if editable_options:
                selected_edit_label = st.selectbox("Select update to modify", list(editable_options.keys()))
                edit_id = editable_options[selected_edit_label]
                target_update = next((x for x in my_updates if x["id"] == edit_id), None)

                if target_update:
                    with st.form("edit_update_form"):
                        st.write(f"Editing **{target_update.get('task')}** (`{target_update.get('id')}`)")
                        edit_progress = st.slider("Updated Progress %", 0, 100, int(target_update.get("progress", 0)), 5)
                        edit_status = st.selectbox(
                            "Updated Status",
                            ["Not Started", "In Progress", "Blocked", "Completed"],
                            index=["Not Started", "In Progress", "Blocked", "Completed"].index(target_update.get("status", "In Progress"))
                        )
                        edit_desc = st.text_area("Updated Notes", value=target_update.get("description", ""))
                        edit_next = st.text_input("Updated Next Action", value=target_update.get("next_action", ""))
                        btn_update = st.form_submit_button("Save Edits")

                    if btn_update:
                        update_submission(
                            edit_id,
                            {
                                "progress": edit_progress,
                                "status": edit_status,
                                "description": edit_desc.strip(),
                                "next_action": edit_next.strip()
                            },
                            acting_user=current_user
                        )
                        st.session_state.flash_notification = {
                            "title": "Submission Updated Successfully!",
                            "task_id": edit_id,
                            "task_name": target_update.get("task", ""),
                            "project": target_update.get("project_name", ""),
                            "status": edit_status,
                            "progress": edit_progress,
                            "time": datetime.now().strftime("%I:%M %p")
                        }
                        st.rerun()
            else:
                st.info("All your tasks are currently marked completed! Submit a new task to track progress.")


# ==============================================================================
# MANAGER DASHBOARD
# ==============================================================================

elif user_role == "manager":
    all_updates = get_updates()
    all_projects = get_all_projects()
    metrics = compute_metrics(all_updates)

    # Hero Banner
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-tag"><span>●</span> EXECUTIVE COMMAND CENTER</div>
        <div class="hero-title">Manager Operations Dashboard</div>
        <div class="hero-subtitle">Real-time team telemetry • Rule-based risk engine • Automated stand-up briefings and decision logging.</div>
    </div>
    """, unsafe_allow_html=True)

    # Executive Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Active Projects", len(all_projects))
    c2.metric("Total Updates", metrics["total_updates"])
    c3.metric("Completed", metrics["completed"])
    c4.metric("Active Blockers", metrics["blocked"])
    c5.metric("Overdue Tasks", metrics["overdue"])
    c6.metric("🔴 High Risk", metrics["high_risk"])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Flash Toast Notification Display for Manager
    if st.session_state.get("flash_notification"):
        notif = st.session_state["flash_notification"]
        st.toast(f"📋 {notif.get('title', 'Action Saved!')} — Task {notif.get('task_id', '')}", icon="✅")
        st.session_state["flash_notification"] = None

    m_tab_analytics, m_tab_tracker, m_tab_risks, m_tab_actions, m_tab_ai = st.tabs([
        "📊 Visual Analytics",
        "📋 Team Updates Tracker",
        "⚠️ Risk Monitoring & Evidence",
        "✍️ Manager Action Panel",
        "🤖 AI Stand-up Assistant & Reports"
    ])

    # --- TAB 1: VISUAL ANALYTICS ---
    with m_tab_analytics:
        if not all_updates:
            st.info("No data available yet to display charts.")
        else:
            col_chart1, col_chart2 = st.columns(2)

            # Chart 1: Task Status Distribution (Donut Chart)
            status_counts = pd.Series([u.get("status", "Unknown") for u in all_updates]).value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig_status = px.pie(
                status_counts,
                names="Status",
                values="Count",
                title="Task Status Distribution",
                hole=0.55,
                color="Status",
                color_discrete_map={
                    "Completed": "#10b981",
                    "In Progress": "#6366f1",
                    "Blocked": "#f43f5e",
                    "Not Started": "#94a3b8"
                }
            )
            fig_status.update_layout(
                font_family="Plus Jakarta Sans",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            col_chart1.plotly_chart(fig_status, use_container_width=True)

            # Chart 2: Risk Level Breakdown
            risk_levels = [evaluate_task_risk(u)["risk_level"] for u in all_updates]
            risk_counts = pd.Series(risk_levels).value_counts().reindex(["High", "Medium", "Low"]).fillna(0).reset_index()
            risk_counts.columns = ["Risk Level", "Count"]

            fig_risk = px.bar(
                risk_counts,
                x="Risk Level",
                y="Count",
                title="Automated Risk Classification Breakdown",
                color="Risk Level",
                color_discrete_map={
                    "High": "#f43f5e",
                    "Medium": "#f59e0b",
                    "Low": "#10b981"
                }
            )
            fig_risk.update_layout(
                font_family="Plus Jakarta Sans",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=20, l=20, r=20),
                xaxis_title="Risk Severity",
                yaxis_title="Number of Tasks"
            )
            col_chart2.plotly_chart(fig_risk, use_container_width=True)

            # Chart 3: Progress by Project
            proj_data = []
            for u in all_updates:
                proj_data.append({
                    "Project": u.get("project_name", "General"),
                    "Progress": int(u.get("progress", 0)),
                    "Task": u.get("task")
                })
            df_proj = pd.DataFrame(proj_data)
            avg_proj = df_proj.groupby("Project")["Progress"].mean().reset_index()

            fig_bar = px.bar(
                avg_proj,
                x="Project",
                y="Progress",
                title="Average Progress % by Project",
                text="Progress",
                color="Progress",
                color_continuous_scale="Purples"
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.update_layout(
                font_family="Plus Jakarta Sans",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_range=[0, 115],
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TAB 2: TEAM UPDATES TRACKER ---
    with m_tab_tracker:
        # Filters
        f1, f2, f3, f4 = st.columns(4)
        proj_filter = f1.selectbox("Filter by Project", ["All"] + [p["name"] for p in all_projects])
        emp_filter = f2.selectbox("Filter by Employee", ["All"] + sorted(list(set(u.get("employee", "") for u in all_updates if u.get("employee")))))
        status_filter = f3.selectbox("Filter by Status", ["All", "In Progress", "Blocked", "Completed", "Not Started"])
        risk_filter = f4.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])

        search_query = st.text_input("🔍 Search", placeholder="Search keyword, ID, person, project, blocker, decision...")

        table_rows = []
        for u in all_updates:
            risk_eval = evaluate_task_risk(u)
            table_rows.append({
                "ID": u.get("id"),
                "Employee": u.get("employee"),
                "Project": u.get("project_name"),
                "Task": u.get("task"),
                "Status": u.get("status"),
                "Progress %": u.get("progress"),
                "Due Date": u.get("due_date") or "N/A",
                "Blocker": u.get("blocker"),
                "Risk Level": risk_eval["risk_level"],
                "Risk Category": risk_eval["category"],
                "Manager Decision": u.get("manager_decision", "Pending review"),
                "Manager Comment": u.get("manager_comment", ""),
                "Last Updated": u.get("updated_at", u.get("created_at")),
                "Description": u.get("description", ""),
                "Blocker Details": u.get("blocker_desc", "")
            })

        df_all = pd.DataFrame(table_rows)

        if not df_all.empty:
            if proj_filter != "All":
                df_all = df_all[df_all["Project"] == proj_filter]
            if emp_filter != "All":
                df_all = df_all[df_all["Employee"] == emp_filter]
            if status_filter != "All":
                df_all = df_all[df_all["Status"] == status_filter]
            if risk_filter != "All":
                df_all = df_all[df_all["Risk Level"] == risk_filter]
            if search_query.strip():
                q = search_query.strip().lower()
                # Search across all columns
                search_mask = df_all.astype(str).apply(
                    lambda col: col.str.lower().str.contains(q, na=False, regex=False)
                ).any(axis=1)
                df_all = df_all[search_mask]

            display_cols = [
                "ID", "Employee", "Project", "Task", "Status", "Progress %",
                "Due Date", "Blocker", "Risk Level", "Risk Category", "Manager Decision",
                "Manager Comment", "Last Updated", "Description", "Blocker Details"
            ]

            if not df_all.empty:
                st.dataframe(df_all[display_cols], use_container_width=True, hide_index=True)

                csv_data = df_all[display_cols].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Filtered Updates (CSV)",
                    data=csv_data,
                    file_name=f"team_project_updates_{date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No updates match the search or filter criteria.")
        else:
            st.info("No updates match the selected filters.")

    # --- TAB 3: RISK MONITORING & EVIDENCE ---
    with m_tab_risks:
        high_risk_tasks = []
        medium_risk_tasks = []
        low_risk_tasks = []

        for u in all_updates:
            risk = evaluate_task_risk(u)
            item = {**u, "_risk": risk}
            if risk["risk_level"] == "High":
                high_risk_tasks.append(item)
            elif risk["risk_level"] == "Medium":
                medium_risk_tasks.append(item)
            else:
                low_risk_tasks.append(item)

        st.markdown(f"#### 🔴 High Priority Risks ({len(high_risk_tasks)} items)")
        if high_risk_tasks:
            for item in high_risk_tasks:
                r = item["_risk"]
                with st.expander(f"🔴 [{item['id']}] {item.get('task')} — {r['category']} (Assignee: {item.get('employee')})", expanded=True):
                    col_r1, col_r2 = st.columns([1, 1])
                    with col_r1:
                        st.markdown(f"**Trigger Reason:** {r['reason']}")
                        st.markdown(f"**Supporting Evidence:** `{r['evidence']}`")
                        st.markdown(f"**Project:** {item.get('project_name')} | **Status:** {item.get('status')}")
                    with col_r2:
                        st.markdown(f"**Recommended Action:** {r['suggested_action']}")
                        st.markdown(f"**Current Manager Decision:** `{item.get('manager_decision', 'Pending review')}`")
                        if item.get("manager_comment"):
                            st.info(f"Manager Note: {item.get('manager_comment')}")
        else:
            st.success("✅ No high priority blockers or overdue deliveries currently detected.")

        st.markdown(f"#### 🟡 Medium Watchlist Risks ({len(medium_risk_tasks)} items)")
        if medium_risk_tasks:
            for item in medium_risk_tasks:
                r = item["_risk"]
                with st.expander(f"🟡 [{item['id']}] {item.get('task')} — {r['category']} (Assignee: {item.get('employee')})"):
                    st.markdown(f"**Trigger Reason:** {r['reason']}")
                    st.markdown(f"**Evidence:** `{r['evidence']}`")
                    st.markdown(f"**Recommended Action:** {r['suggested_action']}")
        else:
            st.info("No medium-level delivery risks or bottlenecks detected.")

    # --- TAB 4: MANAGER ACTION PANEL ---
    with m_tab_actions:
        if not all_updates:
            st.info("No updates available to review.")
        else:
            update_options = {
                f"{u['id']} | {u.get('employee')} | {u.get('task')} [{u.get('status')}]": u['id']
                for u in all_updates
            }
            selected_label = st.selectbox("Select update to record decision", list(update_options.keys()))
            selected_id = update_options[selected_label]
            selected_update = next(x for x in all_updates if x["id"] == selected_id)
            selected_risk = evaluate_task_risk(selected_update)

            col_detail1, col_detail2 = st.columns(2)
            with col_detail1:
                st.markdown(f"**Employee:** {selected_update.get('employee')}")
                st.markdown(f"**Project:** {selected_update.get('project_name')}")
                st.markdown(f"**Task Description:** {selected_update.get('description')}")
                st.markdown(f"**Reported Blocker:** {selected_update.get('blocker_desc') or 'None'}")
                st.markdown(f"**Dependency:** {selected_update.get('dependency') or 'None'}")

            with col_detail2:
                st.markdown(f"**Automated Risk Level:** `{selected_risk['risk_level']}` ({selected_risk['category']})")
                st.markdown(f"**Risk Evidence:** {selected_risk['evidence']}")
                st.markdown(f"**Engine Suggestion:** {selected_risk['suggested_action']}")
                st.markdown(f"**Employee Next Action:** {selected_update.get('next_action')}")

            st.divider()

            with st.form("manager_decision_form"):
                decisions_list = [
                    "Pending review",
                    "Confirmed blocker",
                    "Potential risk",
                    "Not a risk",
                    "Need more information",
                    "Resolved"
                ]
                current_dec = selected_update.get("manager_decision", "Pending review")
                curr_idx = decisions_list.index(current_dec) if current_dec in decisions_list else 0

                new_decision = st.selectbox("Manager Decision *", decisions_list, index=curr_idx)
                manager_comment = st.text_area(
                    "Manager Comments & Unblocking Directives *",
                    value=selected_update.get("manager_comment", ""),
                    placeholder="Enter explicit steps taken, notes from unblocking discussions, or instructions..."
                )
                followup_date = st.date_input("Follow-up Target Date", value=date.today())

                save_action = st.form_submit_button("Save Manager Decision to Database", type="primary")

            if save_action:
                if not manager_comment.strip() and new_decision in ("Confirmed blocker", "Resolved"):
                    st.warning("Please include a brief note explaining the action taken.")
                else:
                    record_manager_action(
                        selected_id,
                        decision=new_decision,
                        comment=manager_comment.strip(),
                        followup_date=str(followup_date)
                    )
                    st.session_state.flash_notification = {
                        "title": "Manager Review Recorded!",
                        "task_id": selected_id,
                        "task_name": selected_update.get("task", ""),
                        "status": new_decision,
                        "time": datetime.now().strftime("%I:%M %p")
                    }
                    st.rerun()

    # --- TAB 5: AI STAND-UP ASSISTANT & REPORTS ---
    with m_tab_ai:
        col_q1, col_q2, col_q3 = st.columns(3)
        btn_briefing = col_q1.button("📋 Generate Daily Briefing", use_container_width=True)
        btn_blockers = col_q2.button("🛡️ Analyze Blockers & Dependencies", use_container_width=True)
        btn_urgent = col_q3.button("⚡ List Urgent Action Items", use_container_width=True)

        # State storage for report type
        if "ai_report_type" not in st.session_state:
            st.session_state.ai_report_type = "briefing"

        if btn_briefing:
            st.session_state.ai_report_type = "briefing"
        elif btn_blockers:
            st.session_state.ai_report_type = "blockers"
        elif btn_urgent:
            st.session_state.ai_report_type = "urgent"

        report_type = st.session_state.ai_report_type
        report_html = build_executive_report_ui(report_type, all_updates)

        # Render directly as rich visual content (never code block)
        st.html(report_html)
