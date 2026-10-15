"""
ai_assistant.py
---------------
AI and Rule-Based Project Coordination Assistant.
Generates executive briefings, stand-up summaries, blocker analyses,
and recommended next actions. Supports optional external LLMs (Gemini / OpenAI)
with a deterministic, factual, zero-cost rule-based fallback engine.
"""

import os
import json
import requests
import html
from datetime import date
from typing import List, Dict, Any
from risk_engine import evaluate_task_risk, compute_metrics


def _clean_html(raw_html: str) -> str:
    """Strips leading whitespace from each line so Streamlit never treats HTML as Markdown code blocks."""
    return "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())


def build_executive_report_ui(query_type: str, updates: List[Dict[str, Any]]) -> str:
    """Builds a bespoke, high-end executive dashboard UI (HTML) with zero raw markdown or ChatGPT feel."""
    today_str = date.today().strftime("%B %d, %Y")
    if not updates:
        return _clean_html(f"""
        <div class="exec-dashboard">
            <div class="exec-header">
                <div class="exec-title-row">
                    <div class="exec-badge"><span class="pulse-dot"></span><span>EXECUTIVE INTELLIGENCE</span></div>
                    <div class="exec-meta-chips"><span class="exec-chip">📅 {today_str}</span></div>
                </div>
                <div class="exec-title">Project Stand-up & Delivery Briefing</div>
            </div>
            <div class="empty-banner-clean">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">📋</div>
                <div style="font-weight: 700; color: #1e293b;">No Updates Submitted Yet</div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">Submit daily stand-up records to synthesize executive briefings and risk analytics.</div>
            </div>
        </div>
        """)

    metrics = compute_metrics(updates)
    evaluated = []
    for u in updates:
        risk = evaluate_task_risk(u)
        evaluated.append({**u, "_risk": risk})

    high_risks = [x for x in evaluated if x["_risk"]["risk_level"] == "High"]
    medium_risks = [x for x in evaluated if x["_risk"]["risk_level"] == "Medium"]
    completed = [x for x in evaluated if str(x.get("status", "")).lower() == "completed"]
    in_progress = [x for x in evaluated if str(x.get("status", "")).lower() == "in progress"]

    if query_type == "blockers":
        blocked_items = [
            x for x in evaluated 
            if x["_risk"]["category"] in ("Active Blocker", "Dependency Bottleneck") 
            or str(x.get("blocker", "")).lower() in ("yes", "true", "1")
            or str(x.get("status", "")).lower() == "blocked"
        ]
        
        cards_html = ""
        if blocked_items:
            for item in blocked_items:
                r = item["_risk"]
                tid = html.escape(str(item.get("id", "")))
                tname = html.escape(str(item.get("task", "Untitled Deliverable")))
                emp = html.escape(str(item.get("employee", "Unassigned")))
                proj = html.escape(str(item.get("project_name", "General")))
                bdesc = html.escape(str(item.get("blocker_desc") or "Unspecified blocker details"))
                dep = html.escape(str(item.get("dependency") or "None"))
                act = html.escape(str(r.get("suggested_action", "")))

                cards_html += f"""
                <div class="exec-alert-card">
                    <div class="exec-card-top">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="task-pill">{tid}</span>
                            <span class="task-name">{tname}</span>
                        </div>
                        <span class="badge-category-red">Active Blocker</span>
                    </div>
                    <div class="exec-card-meta">
                        <span class="meta-item">👤 <strong>Assignee:</strong> {emp}</span>
                        <span class="meta-item">📁 <strong>Project:</strong> {proj}</span>
                        <span class="meta-item">🔗 <strong>Dependency:</strong> {dep}</span>
                    </div>
                    <div class="evidence-box">
                        <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #b91c1c; margin-bottom: 4px;">⚠️ Blocker Details</div>
                        <div>{bdesc}</div>
                    </div>
                    <div class="action-box">
                        <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #4338ca; margin-bottom: 4px;">⚡ Recommended Next Action</div>
                        <div>{act}</div>
                    </div>
                </div>
                """
        else:
            cards_html = """
            <div class="empty-banner-clean">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">🎉</div>
                <div style="font-weight: 700; color: #1e293b;">Zero Blockers Active</div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">All deliverables across projects are progressing unhindered.</div>
            </div>
            """

        return _clean_html(f"""
        <div class="exec-dashboard">
            <div class="exec-header">
                <div class="exec-title-row">
                    <div class="exec-badge" style="background: rgba(239, 68, 68, 0.1); color: #dc2626; border-color: rgba(239, 68, 68, 0.25);">
                        <span class="pulse-dot" style="background-color: #ef4444;"></span>
                        <span>BLOCKER & DEPENDENCY INSPECTOR</span>
                    </div>
                    <div class="exec-meta-chips">
                        <span class="exec-chip">🛑 {len(blocked_items)} Flagged Blocker(s)</span>
                        <span class="exec-chip">📅 {today_str}</span>
                    </div>
                </div>
                <div class="exec-title">Active Blockers & Cross-Functional Bottlenecks</div>
                <div class="exec-subtitle">Immediate engineering impediments extracted from daily verified stand-up logs.</div>
            </div>
            {cards_html}
        </div>
        """)

    elif query_type == "urgent":
        cards_html = ""
        if high_risks:
            for item in high_risks:
                r = item["_risk"]
                tid = html.escape(str(item.get("id", "")))
                tname = html.escape(str(item.get("task", "Untitled Deliverable")))
                emp = html.escape(str(item.get("employee", "Unassigned")))
                proj = html.escape(str(item.get("project_name", "General")))
                reason = html.escape(str(r.get("reason", "")))
                ev = html.escape(str(r.get("evidence", "")))
                act = html.escape(str(r.get("suggested_action", "")))

                cards_html += f"""
                <div class="exec-alert-card">
                    <div class="exec-card-top">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="task-pill">{tid}</span>
                            <span class="task-name">{tname}</span>
                        </div>
                        <span class="badge-category-red">High Priority Escalation</span>
                    </div>
                    <div class="exec-card-meta">
                        <span class="meta-item">👤 <strong>Assignee:</strong> {emp}</span>
                        <span class="meta-item">📁 <strong>Project:</strong> {proj}</span>
                        <span class="meta-item">⚠️ <strong>Category:</strong> {html.escape(r.get("category", "Risk"))}</span>
                    </div>
                    <div class="evidence-box">
                        <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #b91c1c; margin-bottom: 4px;">🔍 Empirical Trigger & Evidence</div>
                        <div><strong>Reason:</strong> {reason}</div>
                        <div style="margin-top: 4px; color: #475569;"><strong>Evidence:</strong> {ev}</div>
                    </div>
                    <div class="action-box">
                        <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #4338ca; margin-bottom: 4px;">⚡ Executive Resolution Directive</div>
                        <div>{act}</div>
                    </div>
                </div>
                """
        else:
            cards_html = """
            <div class="empty-banner-clean">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">✅</div>
                <div style="font-weight: 700; color: #1e293b;">No Urgent Escalations</div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">All deliverables are currently operating within acceptable velocity parameters.</div>
            </div>
            """

        return _clean_html(f"""
        <div class="exec-dashboard">
            <div class="exec-header">
                <div class="exec-title-row">
                    <div class="exec-badge" style="background: rgba(244, 63, 94, 0.1); color: #e11d48; border-color: rgba(244, 63, 94, 0.25);">
                        <span class="pulse-dot" style="background-color: #f43f5e;"></span>
                        <span>URGENT ESCALATION QUEUE</span>
                    </div>
                    <div class="exec-meta-chips">
                        <span class="exec-chip">🚨 {len(high_risks)} Critical Items</span>
                        <span class="exec-chip">📅 {today_str}</span>
                    </div>
                </div>
                <div class="exec-title">Critical Attention Queue & Immediate Actions</div>
                <div class="exec-subtitle">Prioritized delivery deliverables needing swift intervention to avoid milestone slip.</div>
            </div>
            {cards_html}
        </div>
        """)

    # Default: Full Executive Briefing
    critical_html = ""
    if high_risks:
        for item in high_risks:
            r = item["_risk"]
            tid = html.escape(str(item.get("id", "")))
            tname = html.escape(str(item.get("task", "Untitled Deliverable")))
            emp = html.escape(str(item.get("employee", "Unassigned")))
            proj = html.escape(str(item.get("project_name", "General")))
            status = html.escape(str(item.get("status", "In Progress")))
            prog = item.get("progress", 0)
            ev = html.escape(str(r.get("evidence", "")))
            act = html.escape(str(r.get("suggested_action", "")))

            critical_html += f"""
            <div class="exec-alert-card">
                <div class="exec-card-top">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="task-pill">{tid}</span>
                        <span class="task-name">{tname}</span>
                    </div>
                    <span class="badge-category-red">{html.escape(r.get("category", "High Risk"))}</span>
                </div>
                <div class="exec-card-meta">
                    <span class="meta-item">👤 <strong>Assignee:</strong> {emp}</span>
                    <span class="meta-item">📁 <strong>Project:</strong> {proj}</span>
                    <span class="meta-item">⏳ <strong>Status:</strong> {status} ({prog}%)</span>
                </div>
                <div class="evidence-box">
                    <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #b91c1c; margin-bottom: 4px;">🔍 Supporting Evidence</div>
                    <div>{ev}</div>
                </div>
                <div class="action-box">
                    <div style="font-weight: 700; font-size: 0.78rem; text-transform: uppercase; color: #4338ca; margin-bottom: 4px;">⚡ Recommended Manager Action</div>
                    <div>{act}</div>
                </div>
            </div>
            """
    else:
        critical_html = """
        <div class="empty-banner-clean">
            <div style="font-size: 1.5rem; margin-bottom: 4px;">✅</div>
            <div style="font-weight: 700; color: #166534;">No Critical Blockers or Overdue Deliverables</div>
            <div style="font-size: 0.85rem; color: #15803d; margin-top: 2px;">Active milestones across all projects are progressing on schedule.</div>
        </div>
        """

    watchlist_html = ""
    if medium_risks:
        for item in medium_risks:
            r = item["_risk"]
            tid = html.escape(str(item.get("id", "")))
            tname = html.escape(str(item.get("task", "Untitled Deliverable")))
            emp = html.escape(str(item.get("employee", "Unassigned")))
            proj = html.escape(str(item.get("project_name", "General")))
            reason = html.escape(str(r.get("reason", "")))
            act = html.escape(str(r.get("suggested_action", "")))
            cat = html.escape(str(r.get("category", "Watchlist")))

            watchlist_html += f"""
            <div class="watchlist-card">
                <div class="watchlist-title">
                    <span class="task-pill" style="background: #334155;">{tid}</span>
                    <span>{tname}</span>
                    <span class="badge-category-amber">{cat}</span>
                </div>
                <div class="watchlist-desc"><strong>Observation:</strong> {reason}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-top: 6px;">
                    <span class="watchlist-action">🎯 Action: {act}</span>
                    <span style="font-size: 0.78rem; color: #64748b;">👤 {emp} · 📁 {proj}</span>
                </div>
            </div>
            """
    else:
        watchlist_html = """
        <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #64748b; text-align: center;">
            No velocity bottlenecks or secondary risk triggers detected.
        </div>
        """

    blocked_kpi_class = "kpi-card kpi-danger" if metrics['blocked'] > 0 else "kpi-card"
    overdue_kpi_class = "kpi-card kpi-warning" if metrics['overdue'] > 0 else "kpi-card"

    return _clean_html(f"""
    <div class="exec-dashboard">
        <!-- Header -->
        <div class="exec-header">
            <div class="exec-title-row">
                <div class="exec-badge">
                    <span class="pulse-dot"></span>
                    <span>EXECUTIVE MEMO • SYNTHESIZED BRIEFING</span>
                </div>
                <div class="exec-meta-chips">
                    <span class="exec-chip">📅 {today_str}</span>
                    <span class="exec-chip" style="background: #f0fdf4; border-color: #bbf7d0; color: #166534;">🛡️ Verified DB Records</span>
                </div>
            </div>
            <div class="exec-title">Executive Project Stand-up Briefing</div>
            <div class="exec-subtitle">Continuous Multi-Factor Synthesis of Delivery Velocity, Risk Factors & Team Blockers.</div>
        </div>

        <!-- Section 1: Executive KPI Health -->
        <div class="exec-section-header">
            <span>📊</span>
            <span>Executive Delivery Health</span>
        </div>
        <div class="exec-kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Updates</div>
                <div class="kpi-value" style="color: #4f46e5;">{metrics['total_updates']}</div>
                <div class="kpi-sub">Across all projects</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">In Progress</div>
                <div class="kpi-value" style="color: #0284c7;">{len(in_progress)}</div>
                <div class="kpi-sub">Active work streams</div>
            </div>
            <div class="kpi-card kpi-success">
                <div class="kpi-label">Completed</div>
                <div class="kpi-value" style="color: #16a34a;">{metrics['completed']}</div>
                <div class="kpi-sub">Delivered milestones</div>
            </div>
            <div class="{blocked_kpi_class}">
                <div class="kpi-label">Active Blockers</div>
                <div class="kpi-value" style="color: #dc2626;">{metrics['blocked']}</div>
                <div class="kpi-sub">Requiring clearance</div>
            </div>
            <div class="{overdue_kpi_class}">
                <div class="kpi-label">Overdue Tasks</div>
                <div class="kpi-value" style="color: #d97706;">{metrics['overdue']}</div>
                <div class="kpi-sub">Past target deadline</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Pending Reviews</div>
                <div class="kpi-value" style="color: #7c3aed;">{metrics['pending_reviews']}</div>
                <div class="kpi-sub">Awaiting sign-off</div>
            </div>
        </div>

        <!-- Section 2: Critical Items Requiring Attention -->
        <div class="exec-section-header" style="margin-top: 24px;">
            <span>🚨</span>
            <span>Critical Items Requiring Immediate Attention ({len(high_risks)})</span>
        </div>
        {critical_html}

        <!-- Section 3: Delivery Watchlist -->
        <div class="exec-section-header" style="margin-top: 24px;">
            <span>🟡</span>
            <span>Delivery Watchlist & Dependency Bottlenecks ({len(medium_risks)})</span>
        </div>
        {watchlist_html}
    </div>
    """)


def _build_rule_based_briefing(updates: List[Dict[str, Any]]) -> str:
    """Deterministic, grounded rule-based summary when no LLM is configured."""
    if not updates:
        return "### 📋 Executive Project Briefing\n\nNo stand-up updates have been submitted yet."

    metrics = compute_metrics(updates)
    evaluated = []
    for u in updates:
        risk = evaluate_task_risk(u)
        evaluated.append({**u, "_risk": risk})

    high_risks = [x for x in evaluated if x["_risk"]["risk_level"] == "High"]
    medium_risks = [x for x in evaluated if x["_risk"]["risk_level"] == "Medium"]
    completed = [x for x in evaluated if str(x.get("status", "")).lower() == "completed"]
    in_progress = [x for x in evaluated if str(x.get("status", "")).lower() == "in progress"]

    lines = [
        "### 🚀 Executive Project Stand-up Briefing",
        "> *[Mode: Rule-Based Fallback Engine — Factual & Deterministic]*",
        "",
        "#### 1. Executive Summary",
        f"- **Total Updates Tracked:** {metrics['total_updates']}",
        f"- **Active In Progress:** {len(in_progress)} | **Completed:** {metrics['completed']}",
        f"- **Blockers Reported:** {metrics['blocked']} | **Overdue Tasks:** {metrics['overdue']}",
        f"- **Risk Distribution:** 🔴 {metrics['high_risk']} High · 🟡 {metrics['medium_risk']} Medium · 🟢 {metrics['low_risk']} Low",
        f"- **Pending Manager Reviews:** {metrics['pending_reviews']}",
        "",
        "#### 2. Critical Items Requiring Immediate Attention",
    ]

    if high_risks:
        for idx, item in enumerate(high_risks, 1):
            r = item["_risk"]
            lines.append(
                f"{idx}. **[{item['id']}] {item.get('task', 'Untitled')}** (Assignee: *{item.get('employee', 'Unassigned')}*)\n"
                f"   - **Category:** {r['category']}\n"
                f"   - **Evidence:** {r['evidence']}\n"
                f"   - **Recommended Action:** {r['suggested_action']}"
            )
    else:
        lines.append("- ✅ No critical blockers or overdue tasks detected across active submissions.")

    lines.append("\n#### 3. Delivery Watchlist & Dependency Bottlenecks")
    if medium_risks:
        for idx, item in enumerate(medium_risks, 1):
            r = item["_risk"]
            lines.append(
                f"- **[{item['id']}] {item.get('task')}** — {r['category']}: {r['reason']} *(Action: {r['suggested_action']})*"
            )
    else:
        lines.append("- ✅ No immediate dependency bottlenecks or stale updates flagged.")

    lines.append("\n#### 4. Manager Next Best Actions")
    actions = []
    if high_risks:
        actions.append("- Coordinate immediate unblocking sessions for flagged High-risk items above.")
    if metrics["pending_reviews"] > 0:
        actions.append(f"- Complete manager review sign-off for {metrics['pending_reviews']} pending update(s).")
    if metrics["completed"] > 0:
        actions.append("- Confirm release verification for completed deliverables.")
    if not actions:
        actions.append("- Continue standard milestone cadence.")

    lines.extend(actions)
    lines.append("\n---\n*Report generated based solely on verified database records. Zero hallucination guaranteed.*")
    return "\n".join(lines)


def query_ai_assistant(query_type: str, updates: List[Dict[str, Any]], custom_prompt: str = "") -> str:
    """
    Queries the AI Assistant. Checks for LLM API keys first;
    gracefully falls back to the deterministic rule-based assistant.
    """
    # 1. Check if Gemini or OpenAI API keys exist
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    # If no key, return rule-based answer
    if not gemini_key and not openai_key:
        return _handle_rule_based_queries(query_type, updates, custom_prompt)

    # Attempt LLM call
    try:
        if gemini_key:
            return _call_gemini(gemini_key, query_type, updates, custom_prompt)
        elif openai_key:
            return _call_openai(openai_key, query_type, updates, custom_prompt)
    except Exception as err:
        fallback_msg = f"> ⚠️ *LLM API request could not be completed ({err}). Displaying rule-based synthesis instead:*\n\n"
        return fallback_msg + _handle_rule_based_queries(query_type, updates, custom_prompt)

    return _handle_rule_based_queries(query_type, updates, custom_prompt)


def _handle_rule_based_queries(query_type: str, updates: List[Dict[str, Any]], custom_prompt: str) -> str:
    if query_type == "briefing":
        return _build_rule_based_briefing(updates)

    elif query_type == "blockers":
        blocked_items = []
        for u in updates:
            risk = evaluate_task_risk(u)
            if risk["category"] in ("Active Blocker", "Dependency Bottleneck") or str(u.get("blocker", "")).lower() == "yes":
                blocked_items.append((u, risk))
        
        if not blocked_items:
            return "### 🛡️ Blocker & Bottleneck Analysis\n\nNo active blockers or unresolved dependencies found in the current updates."

        lines = [
            "### 🛡️ Blocker & Bottleneck Analysis",
            "> *[Rule-Based Assistant Fallback]*",
            "",
            "The following items require coordination to unblock engineering progress:",
            ""
        ]
        for u, r in blocked_items:
            lines.append(
                f"- **{u.get('task')}** (`{u.get('id')}`)\n"
                f"  - **Owner:** {u.get('employee')}\n"
                f"  - **Blocker Detail:** {u.get('blocker_desc') or 'Unspecified blocker'}\n"
                f"  - **Dependency:** {u.get('dependency') or 'None listed'}\n"
                f"  - **Recommended Action:** {r['suggested_action']}\n"
            )
        return "\n".join(lines)

    elif query_type == "urgent":
        highs = [u for u in updates if evaluate_task_risk(u)["risk_level"] == "High"]
        if not highs:
            return "### ⚡ Urgent Action Items\n\nAll tasks are currently within acceptable delivery bounds. No urgent escalations."
        lines = [
            "### ⚡ Urgent Action Items (High Priority)",
            "> *[Rule-Based Assistant Fallback]*",
            ""
        ]
        for u in highs:
            r = evaluate_task_risk(u)
            lines.append(
                f"1. **{u.get('task')}** (ID: `{u.get('id')}`) — Owner: **{u.get('employee')}**\n"
                f"   - **Issue:** {r['reason']}\n"
                f"   - **Evidence:** {r['evidence']}\n"
                f"   - **Action:** {r['suggested_action']}\n"
            )
        return "\n".join(lines)

    else:
        # Default to overall briefing
        return _build_rule_based_briefing(updates)


def _call_gemini(api_key: str, query_type: str, updates: List[Dict[str, Any]], custom_prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload_data = [
        {
            "id": u.get("id"),
            "employee": u.get("employee"),
            "task": u.get("task"),
            "status": u.get("status"),
            "progress": u.get("progress"),
            "blocker": u.get("blocker"),
            "blocker_desc": u.get("blocker_desc"),
            "dependency": u.get("dependency"),
            "due_date": u.get("due_date"),
            "next_action": u.get("next_action")
        }
        for u in updates
    ]

    system_instruction = (
        "You are an AI project coordination assistant. Use ONLY the supplied project update records. "
        "Do NOT invent dates, owners, blockers, or progress. "
        "For risks, provide the exact supporting evidence from the records. "
        "Format clearly with Markdown headers, bullet points, and actionable next steps."
    )

    prompt = f"{system_instruction}\n\nTask Updates Data:\n{json.dumps(payload_data, indent=2)}\n\nQuery: {custom_prompt or query_type}"

    req_body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(url, json=req_body, timeout=12)
    res.raise_for_status()
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai(api_key: str, query_type: str, updates: List[Dict[str, Any]], custom_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload_data = [
        {
            "id": u.get("id"),
            "employee": u.get("employee"),
            "task": u.get("task"),
            "status": u.get("status"),
            "progress": u.get("progress"),
            "blocker": u.get("blocker"),
            "blocker_desc": u.get("blocker_desc"),
            "dependency": u.get("dependency"),
            "due_date": u.get("due_date"),
            "next_action": u.get("next_action")
        }
        for u in updates
    ]

    prompt = f"Task Updates Data:\n{json.dumps(payload_data, indent=2)}\n\nQuery: {custom_prompt or query_type}"

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI project coordination assistant. Use ONLY the supplied records. "
                    "Do NOT invent owners, deadlines, or progress. Provide exact supporting evidence."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    res = requests.post(url, headers=headers, json=body, timeout=12)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"]
