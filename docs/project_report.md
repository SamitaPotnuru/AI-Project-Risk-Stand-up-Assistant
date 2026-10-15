# Comprehensive Project Report
## AI Project Risk & Stand-up Assistant — Role-Based Employee and Manager Dashboard

**Author:** Raju / NxtWave Engineering Project  
**Date:** October 2026  
**Application Stack:** Python, Streamlit, Pandas, Plotly, JSON  
**Consolidated Google Doc Submission:** See [FINAL_SUBMISSION.md](file:///c:/Users/RAJU/Downloads/AI%20Project%20Risk%20&%20Stand-up%20Assistant/FINAL_SUBMISSION.md)

---

## 1. Executive Summary
Traditional project tracking relies on ad-hoc status meetings, unorganized Slack messages, and static spreadsheets. This causes high operational friction: managers spend 4–8 hours per week chasing updates, while critical delivery blockers remain unaddressed until milestones slip.

The **AI Project Risk & Stand-up Assistant** solves this by centralizing daily project check-ins into an intuitive, role-based web application. It features automated rule-based risk classification, multi-dimensional Plotly analytics, decision logging, and executive briefing synthesis with zero reliance on paid APIs.

---

## 2. Problem Statement
1. **Scattered Information:** Progress updates are dispersed across communication channels, resulting in low visibility.
2. **Delayed Blocker Escalation:** Technical impediments and cross-team dependencies often go unnoticed until deadlines pass.
3. **Manual Reporting Overhead:** Managers manually collate data for leadership briefings, consuming valuable engineering hours.
4. **Lack of Role Separation:** Existing basic tools either grant all users full editing permissions or lack strict personal data isolation.

---

## 3. System Architecture & Modular Design

```text
ai_project_assistant/
├── app.py                # Streamlit user interface, navigation, and role views
├── auth.py               # Authentication, SHA-256 password hashing, RBAC helpers
├── database.py           # Persistent JSON storage, atomic writes, CRUD operations
├── risk_engine.py        # Configurable rule-based risk classification engine
├── ai_assistant.py       # Stand-up briefing generator (LLM & Rule-based fallback)
├── requirements.txt      # Python dependencies
├── db.json               # Seed database for users, projects, and updates
├── workflow_diagram.mmd  # Mermaid workflow diagram
├── AI_PROMPT.md          # AI prompts, test suite, and guardrails
├── FINAL_SUBMISSION.md   # Complete single-document submission file
└── docs/
    ├── project_report.md     # Detailed academic & industry project report
    ├── test_cases.md         # Comprehensive test suite report
    ├── AI_design_log.md      # AI design decisions, prompts, and safeguards
    └── loom_demo_script.md   # Step-by-step video demonstration script
```

### Module Responsibilities:
- **`app.py`:** Main entry point handling UI tabs, charts, validation, and session states.
- **`auth.py`:** Secures user access using constant-time hash comparisons (`hmac.compare_digest`) and controls permissions.
- **`database.py`:** Implements safe atomic JSON persistence using temporary write files (`.tmp`) and atomic file replacement (`os.replace`).
- **`risk_engine.py`:** Applies deterministic heuristic rules to tag tasks as High, Medium, or Low risk with direct evidence.
- **`ai_assistant.py`:** Synthesizes executive briefings and answers stand-up queries. Operates with an offline rule-based synthesis engine or an optional external LLM API.

---

## 4. Key Features & Workflows

### 4.1 Employee Workflow
- **Authenticated Check-in:** Log in with employee credentials (`employee` / `Employee@123` or `alex` / `Alex@123`).
- **Form Submission:** Input project assignment, task title, detailed progress, status, progress slider (0–100%), start/due dates, blocker descriptions, dependencies, and next actions.
- **Validation Engine:** Prevents empty descriptions, ensures 100% progress for completed tasks, and mandates blocker explanations when flagged.
- **Personal History & Audit:** View only personal submissions; edit active tasks while maintaining historical audit records.

### 4.2 Manager Workflow
- **Executive Metrics:** High-level cards for Active Projects, Total Updates, Blockers, Overdue Deliverables, and High-Risk counts.
- **Visual Analytics:** Plotly Donut Chart (Status distribution), Plotly Bar Chart (Risk distribution), and Project Progress charts.
- **Searchable Updates Tracker:** Dynamic multi-filter table (by Project, Employee, Status, Risk Level) with one-click CSV export.
- **Evidence Inspector:** Expandable panels grouping tasks by risk level with exact evidence and suggested managerial actions.
- **Manager Action Panel:** Record managerial decisions (`Confirmed blocker`, `Resolved`, `Potential risk`), unblocking instructions, and follow-up milestones directly into `db.json`.
- **AI Stand-up Assistant:** One-click generation of executive stand-up summaries and downloadable Markdown briefings.

---

## 5. Risk Classification Rules

The engine runs deterministically across all records:
1. **Active Blocker (High Risk):** Explicit blocker indicated or status marked 'Blocked'.
2. **Overdue Schedule (High Risk):** Due date has passed and task is incomplete.
3. **At-Risk Velocity (Medium Risk):** Due date is within 2 days with progress under 50%.
4. **Dependency Bottleneck (Medium Risk):** Active external dependency recorded on an incomplete task.
5. **Stale Update (Medium Risk):** No check-in recorded for 3+ days.
6. **Missing Information (Medium Risk):** Empty progress or undefined status.
7. **On Track (Low Risk):** Normal progress or 100% completed deliverables.

---

## 6. Stage 2: 30-Day Business Review Summary

Following a 30-day pilot across three engineering teams, the solution was evaluated under the operational constraints of **zero additional hiring** and **zero new software purchases**:
1. **Challenge Prioritization:**
   - *Priority 1: AI Precision & Confidence Scoring:* Eliminates false blocker alarms by adding confidence ratings and manager 1-click confirmation.
   - *Priority 2: Zero-Cost Chat Ingestion Webhook:* Native Slack/Teams webhooks eliminate workflow bypassing and drive adoption above 90%.
   - *Priority 3: Adaptive Standardized Templates:* Structured micro-fields normalize reporting variance across backend, frontend, and DevOps teams.
2. **Key Success Metrics:** Consistent Adoption Rate ($\ge 90\%$), Mean Time to Unblock ($\le 16\text{h}$), AI Precision ($\ge 92\%$), Template Adherence ($\ge 95\%$), and Manager Reclaimed Time ($3.5\text{--}5.0\text{ h/week}$).

---

## 7. Security & Data Storage Limitations
- **Local JSON Database:** Ideal for local prototypes, demonstrations, and educational environments. For multi-user concurrent production deployments, PostgreSQL or SQLite with connection pooling should be adopted.
- **Password Security:** SHA-256 with constant-time verification is implemented for the prototype. Production systems should use Argon2 or bcrypt alongside an enterprise Identity Provider (OAuth2 / SAML).

---

## 8. Conclusion
The AI Project Risk & Stand-up Assistant provides a scalable, fact-grounded operational framework. By uniting deterministic risk evaluation, AI synthesis, and direct management unblocking actions, it turns fragmented status reporting into predictable delivery execution.
