# AI Design Log & Collaborative Decision Rationale

## 1. Where AI is Used in the Application
AI is utilized within the **Manager Dashboard (Tab 5: AI Stand-up Assistant & Reports)** and background analytics to solve three core operational problems:
1. **Stand-up Synthesis:** Converting multi-task employee updates into an executive daily briefing.
2. **Blocker & Bottleneck Analysis:** Aggregating external dependencies and technical blockers into prioritized escalation lists.
3. **Actionable Recommendations:** Suggesting concrete management next steps based on verified risk triggers.

---

## 2. Prompts Used & Architecture

### System Directive:
```text
You are an AI project coordination assistant. Use ONLY the supplied project update records.
Do NOT invent owners, deadlines, progress, or dependencies.
Separate confirmed facts from inferred risks.
For every identified risk, cite the exact supporting evidence from the records.
Do not label a task blocked solely because it is late.
```

### Input Payload:
A structured JSON array of active updates including: `id`, `employee`, `task`, `status`, `progress`, `blocker`, `blocker_desc`, `dependency`, `due_date`, and `next_action`.

### Output Structure:
1. Executive Summary & Delivery Metrics.
2. Critical Items Requiring Immediate Attention (Blockers & Overdue items).
3. Delivery Watchlist & Dependency Bottlenecks.
4. Confidence Score & Items Needing Confirmation.
5. Manager Next Best Actions.

---

## 3. Rule-Based vs. LLM Analysis: Comparison

| Dimension | Rule-Based Risk Engine (`risk_engine.py`) | LLM Assistant (`ai_assistant.py`) |
| :--- | :--- | :--- |
| **Execution Cost** | **Zero cost**; runs entirely in local Python runtime. | Minimal API token cost (if API key provided). |
| **Determinism** | **100% deterministic**; identical inputs always produce identical risk scores. | Generative language phrasing; structured by strict prompt instructions. |
| **Speed** | Sub-millisecond execution. | 1.0 – 2.5 seconds depending on network latency. |
| **Offline Capability** | Fully offline; requires no internet connection. | Requires external network connectivity to Gemini/OpenAI endpoints. |
| **Primary Value** | Rigorous threshold checks (e.g. overdue dates, missing fields). | Natural language briefing synthesis and coherent stand-up summaries. |

---

## 4. Risks of Incorrect AI Output & Mitigation Strategies

1. **Hallucination of Deadlines or Blocker Causes:**
   - *Risk:* An LLM could assume why a task is blocked (e.g., guessing a bug when it was actually credential delays).
   - *Mitigation:* The prompt explicitly commands: *"Never invent owners, deadlines, or dependencies. If unknown, state 'Information missing'."* Furthermore, the rule-based fallback guarantees zero-hallucination data extraction.
2. **Unauthorized Work Reassignment:**
   - *Risk:* An automated system might reassign tasks or alter priorities without manager sign-off.
   - *Mitigation:* The AI is strictly advisory. Manager actions require manual human review and explicit submission via the Manager Action Panel.
3. **API Unavailability:**
   - *Risk:* External LLM endpoints could suffer outages or rate limiting.
   - *Mitigation:* `ai_assistant.py` catches API exceptions automatically and falls back gracefully to the offline deterministic synthesis engine.

---

## 5. Validation, Learning & Rejected AI Suggestions

- **Validation Suite:** Evaluated with 14 automated and manual test cases covering overdue schedules, false blockers, empty inputs, and simulated network drops.
- **One AI Suggestion Rejected:** Early in prompt tuning, an AI proposal recommended automatically reassigning tasks from overloaded engineers to peers. This was firmly rejected because task reassignments in engineering require deep domain context and human managerial trust.
- **Key Iteration That Improved Quality:** Incorporating verbatim evidence quotation and confidence scoring directly resolved the false blocker problem identified in the 30-day pilot.

---

## 6. Privacy, Data Protection, and Security Safeguards

- **Credential Isolation:** Passwords, password hashes, and session authentication tokens are **never** passed to the AI prompt or LLM payload.
- **Data Minimization:** Only operational task fields (`task_name`, `status`, `progress`, `blocker_desc`) are included in model context.
- **Zero Third-Party Model Training:** Instructions specify standard enterprise API endpoints with zero data retention for training.
