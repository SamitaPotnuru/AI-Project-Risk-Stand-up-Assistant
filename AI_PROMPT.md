# AI Prompt Engineering & Design Log

## 1. Initial Prompt (Exploratory Stage)
> "Summarize project updates, identify blockers, and create a concise manager report."

### Limitations of Initial Prompt:
- **Hallucination of Dates & Ownership:** Inferred delivery dates, completion percentages, or team assignments not present in the database.
- **Subjective & False Blocker Flagging:** Confused simple non-critical schedule variations with catastrophic blockers.
- **Vague, Non-Actionable Advice:** Produced generic recommendations such as *"The team should focus and work harder to achieve goals."*
- **Absence of Factual Grounding:** Did not distinguish between verified database facts and probabilistic AI interpretations.

---

## 2. Refined Production Prompt (Stage 1)
```text
You are an expert AI Project Operations & Delivery Risk Assistant. Use ONLY the supplied JSON update records.
For each task, return:
- Task ID
- Owner / Assignee
- Normalized status
- Factual summary
- Explicitly reported blockers
- Potential risks with exact supporting evidence
- Missing information or uncertainty
- One targeted follow-up question
- Recommended next action for the manager

CRITICAL GUARDRAILS:
1. Never invent owners, deadlines, progress percentages, or dependencies.
2. Separate confirmed facts from inferred delivery risks.
3. Do not label a task 'Blocked' solely because it is late; only label it 'Blocked' if an explicit blocker was recorded.
4. Flag conflicts and require manager confirmation for critical risk items.
5. If data is missing or incomplete, explicitly state "Information missing" rather than guessing.
6. End with a concise executive stand-up briefing.
```

---

## 3. Stage 2 Prompt Refinements (Addressing the 30-Day Business Review)

To resolve the challenges highlighted by Central Operations (65% adoption, AI context misinterpretations, disparate reporting styles, and leadership metric reliability), the prompt and data schema were upgraded with:

### A. Confidence-Scored Risk & Blocker Extraction Prompt
```text
You are an advanced Project Risk Intelligence Assistant.
Analyze ONLY the provided team status records. 

EVALUATION RULES:
1. BLOCKER VALIDATION:
   - Mark as 'Active Blocker' ONLY if the user explicitly chose a Blocker taxonomy category (Vendor, Dependency, Credentials, Technical Bug) OR status is 'Blocked'.
   - If an impediment is described as a routine wait (e.g., standard CI build duration, scheduled review window), categorize as 'Normal In-Progress Dependency' rather than an Active Blocker.

2. CONFIDENCE SCORING:
   - Provide a confidence score (0% to 100%) for each flagged risk.
   - If confidence is < 85%, tag as [NEEDS_MANAGER_CONFIRMATION] with a suggested clarifying question.

3. STRUCTURED EVIDENCE:
   - For every flagged risk or blocker, quote verbatim the supporting text from the employee's submission under 'Supporting Evidence'.

4. EXECUTIVE BRIEFING:
   - Section 1: Macro Delivery Summary (Total active tasks, verified blockers count, at-risk velocity count).
   - Section 2: Critical Blockers (Requiring immediate unblocking intervention).
   - Section 3: Delivery Watchlist (Approaching deadlines with progress < 50%).
   - Section 4: Manager Next Best Actions (Ranked by delivery impact).
```

### B. Reciprocal Personal Daily Focus Prompt (Boosts Employee Adoption)
```text
Given the employee's submitted check-in for today, generate a 3-bullet "Personal Daily Focus Plan":
- Key Milestone to Clear Today
- Dependency or Resource to Follow-up On
- Relevant unblocking action logged by their Manager (if any)
Keep it under 60 words. Make it encouraging, actionable, and focused on unblocking flow state.
```

---

## 4. Test Cases for Prompt & Assistant Validation

| Test Case | Scenario Description | Expected Assistant Output | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-1** | Waiting for API credentials (`UP-1001`) | Report dependency on Infra Security; recommend checking credential ETA; do not invent ETA. | Highlighted as Active Blocker with verbatim evidence: *"Waiting for production API credentials..."*. | **PASS** |
| **TC-2** | Tests passed 100% (`UP-1002`) | Report completed; classify as Low Risk / On Track; no blocker inferred. | Correctly classified as Completed (Low Risk); suggested release sign-off. | **PASS** |
| **TC-3** | Past due date & In Progress (`UP-1003`) | Report as Overdue Schedule; potential delay flag; do NOT mark as confirmed blocker. | Classified as High Risk (Overdue Schedule) with exact days overdue cited. | **PASS** |
| **TC-4** | Low progress near due date (`UP-1004`) | Flag for At-Risk Velocity review; recommend pair programming or assistance. | Correctly flagged under Medium Watchlist with progress cited as 30%. | **PASS** |
| **TC-5** | Routine wait (CI build queue) | Do NOT classify as critical blocker; categorize as normal in-progress dependency. | Confidence check filters out routine wait; marked as On Track. | **PASS** |
| **TC-6** | Empty progress notes | State "Missing information" rather than assuming failure or hallucinating work. | Rule engine and prompt return "Information Missing". | **PASS** |

---

## 5. Evaluation, Guardrails & Design Decisions

- **AI Tools Used:** Google Gemini 1.5 Flash / OpenAI GPT-4o-mini API with deterministic Python rule-based fallback engine (`risk_engine.py`).
- **Iteration Count:** 6 major iterations tested against realistic edge cases and disparate reporting formats.
- **Knowledge Sources:** Agile/Scrum stand-up best practices, PMI project risk management guidelines, Google SRE blameless post-mortem patterns.
- **Validation Method:** Automated deterministic test suite and cross-verification against seed `db.json` records.
- **AI Suggestion Rejected & Why:** Early models suggested automatically reassigning overdue tasks to colleagues. Rejected to preserve managerial agency, engineering team morale, and task accountability.
- **Key Iteration That Improved Quality:** Mandating verbatim quotation of supporting evidence and adding confidence scoring for human-in-the-loop manager approval.
