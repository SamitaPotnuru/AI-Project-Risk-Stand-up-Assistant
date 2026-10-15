# 🚀 AI Project Risk & Stand-up Assistant
### Role-Based Employee and Manager Dashboard with Automated Risk Engine & AI Briefings

A professional, zero-cost web application built with **Python**, **Streamlit**, **Pandas**, and **Plotly** that centralizes asynchronous daily stand-up check-ins, deterministically detects delivery bottlenecks, equips engineering managers with actionable briefings, and scales seamlessly across multi-squad operations.

---

## 📌 1. Problem Statement
In engineering and cross-functional teams, status updates are fragmented across Slack, emails, and disparate spreadsheets. Critical delivery blockers remain silent until deadlines are missed, while managers spend 4–8 hours per week manually chasing updates and compiling executive reports. 

The **AI Project Risk & Stand-up Assistant** solves this by:
- Centralizing daily check-ins into an intuitive, role-isolated web interface.
- Automatically detecting schedule and technical risks using a zero-hallucination deterministic engine.
- Synthesizing executive daily briefings and unblocking action plans using hybrid AI with offline fallback.

---

## 🎥 2. Solution Walkthrough & Loom Build Demo
- **Video Walkthrough (Loom):** [Watch the End-to-End Build Demonstration](https://www.loom.com/share/demo-ai-project-assistant)
- 
### Why this Solution?
- **Zero Cost & Instant Time-to-Value:** Built in Python & Streamlit; requires no paid SaaS subscriptions or heavy database setups.
- **Hybrid AI Architecture:** Heuristic rules evaluate schedules and blockers with 100% determinism; the LLM focuses purely on executive synthesis and natural language assistance.
- **Closed-Loop Action:** Managers don't just view data—they record official decisions, directives, and follow-ups directly in the platform.

---

## ✨ Features

### 👨‍💻 Employee Workspace
- **Secure Role-Based Authentication:** SHA-256 hashed credentials with constant-time verification.
- **Structured Daily Check-ins:** Project selection, task title, progress slider (0–100%), delivery status, dependencies, blocker flags, and next actions.
- **Strict Form Validation:** Prevents empty descriptions, mandates explicit blocker notes when flagged, and enforces 100% completion rules.
- **Personal History & Isolation:** Employees see only their own updates with complete audit trail visibility.

### 👩‍💼 Manager Dashboard
- **Executive Metric Cards:** Live tallies for Active Projects, Total Updates, Blockers, Overdue Deliverables, and High-Risk items.
- **Interactive Visualizations:** Plotly donut and bar charts for status distribution, risk severity breakdown, and average progress by project.
- **Multi-Filter Tracker:** Dynamic filtering by project, employee, status, or risk severity with instant CSV export.
- **Automated Risk Engine:** Deterministic rule-based evaluation categorizing tasks into High, Medium, and Low risk with verbatim cited evidence.
- **Manager Action Panel:** Record decisions (`Confirmed blocker`, `Resolved`, `Potential risk`), unblocking instructions, and follow-up milestones.
- **AI Stand-up Assistant:** One-click generation of executive stand-up summaries and downloadable Markdown briefings using Gemini/OpenAI or the built-in offline engine.

---

## 📈 30-Day Business Review Summary (Stage 2)

Following a 30-day pilot across three engineering teams, leadership (Head of Central Operations, Riya Sharma) reviewed the system:
- **Pilot Observations:** ~65% adoption rate, AI context misinterpretations, disparate reporting styles across squads, and updates bypassing into informal chat.
- **Zero-Cost Constraints:** No additional hiring, no new software purchases.

### Prioritized Solutions:
1. **AI Precision & Confidence Scoring:** AI outputs confidence scores (0–100%) and highlights items needing manager 1-click confirmation, eliminating false alarms.
2. **Zero-Cost Ingestion Webhook:** Connects existing free Slack/Teams webhook APIs to eliminate chat backchanneling and raise adoption above 90%.
3. **Adaptive Role-Specific Templates:** Standardized micro-templates with blocker taxonomies (e.g., Access, Dependency, Bug, PR Review) tailored per squad.
4. **Reciprocal Personal Daily Focus:** Generates an immediate 3-bullet focus plan back to the engineer upon submission ("Give-to-Get" model).
5. **Leadership KPIs:** Tracks Consistent Adoption Rate ($\ge 90\%$), Mean Time to Unblock ($\le 16\text{h}$), and AI Precision ($\ge 92\%$).

*(Full detailed analysis in [FINAL_SUBMISSION.md](file:///c:/Users/RAJU/Downloads/AI%20Project%20Risk%20&%20Stand-up%20Assistant/FINAL_SUBMISSION.md#5-stage-2--30-day-business-review))*

---

## 🛠️ Technology Stack
- **Language:** Python 3.10+ (Tested on Python 3.14)
- **Web Framework:** [Streamlit](https://streamlit.io/)
- **Data Analysis & Visualization:** [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/python/)
- **Data Persistence:** Local JSON database (`db.json`) with atomic temporary write swaps and automatic backups
- **AI Integration:** Google Gemini / OpenAI API with deterministic rule-based fallback engine

---

## 📂 Project Structure
```text
ai_project_assistant/
├── app.py                # Main Streamlit web application & role routing
├── auth.py               # Authentication, password hashing, session RBAC
├── database.py           # Persistent JSON storage, atomic file operations, CRUD
├── risk_engine.py        # Configurable rule-based risk classification engine
├── ai_assistant.py       # Stand-up briefing generator (LLM & Rule-based fallback)
├── requirements.txt      # Python dependencies
├── db.json               # Seed database for users, projects, and updates
├── workflow_diagram.mmd  # Mermaid workflow diagram (Stage 1 & 2)
├── AI_PROMPT.md          # Complete AI prompt engineering, test cases & logs
├── FINAL_SUBMISSION.md   # Consolidated Google Doc submission artifact
├── .gitignore            # Git ignore configuration
├── .env.example          # Environment variables template
└── docs/
    ├── project_report.md     # Comprehensive project report
    ├── test_cases.md         # 14-point test suite report
    ├── AI_design_log.md      # AI design decisions, prompts, and safeguards
    └── loom_demo_script.md   # 3-5 min video demonstration script
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### 2. Installation
Install all required dependencies:
```bash
python -m pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit application:
```bash
python -m streamlit run app.py
```
Open your browser and navigate to:
👉 **`http://localhost:8501`**

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Assigned Scope |
| :--- | :--- | :--- | :--- |
| **Employee** | `employee` | `Employee@123` | Platform Engineering workspace |
| **Employee** | `alex` | `Alex@123` | Mobile Client workspace |
| **Manager** | `manager` | `Manager@123` | Full cross-team dashboard, risk management & AI briefings |

---

## 💾 Atomic JSON Storage Guarantee
- Updates are saved to `db.tmp` first and swapped to `db.json` via atomic `os.replace`.
- Automatic backup snapshots (`db.backup.json`) are updated upon every save to guarantee zero data loss during sudden process interruptions.
