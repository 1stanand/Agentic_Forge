# Forge Agentic — User Manual

**Last Updated:** 2026-04-27  
**Status:** Backend Ready (Frontend in Development)

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Feature Generation (ATDD)](#feature-generation-atdd)
4. [CAS Assistant (Chat)](#cas-assistant-chat)
5. [Settings & Configuration](#settings--configuration)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

**Forge Agentic** is an AI-powered ATDD (Acceptance Test Driven Development) platform that:

1. **Generates Feature Files** — Converts JIRA stories and requirements into ready-to-execute Gherkin `.feature` files
2. **Grounds Steps in Repository** — Matches generated test steps against your existing feature repository for consistency
3. **CAS Knowledge Assistant** — Answers domain-specific questions using Collateral Assessment System (CAS) documentation
4. **Ordered Flow Support** — Handles complex multi-threaded test scenarios with prerequisite dependencies

### Key Capabilities

| Feature | Use Case | Output |
|---------|----------|--------|
| **Feature Generation** | Convert story → `.feature` file | Complete Gherkin with Given/When/Then/Examples |
| **Step Grounding** | Ensure step consistency | Markers for missing/low-match/role-gap steps |
| **Gap Analysis** | Identify test coverage gaps | Coverage gaps + retrieval gaps report |
| **CAS Assistant** | Ask domain questions | Knowledge-grounded answers from CAS docs |
| **Order Validation** | Test ordered flows | Validates against Order.json + prerequisite structure |

---

## Getting Started

### 1. Login

Visit **http://localhost:8000/** (or your deployment URL)

```
Username: [your username]
Password: [your password]
```

If you don't have credentials, ask your administrator.

### 2. Dashboard Overview

Once logged in, you'll see:

- **Feature Generation** — Start new feature file generation
- **Chat** — Ask CAS domain questions
- **My Sessions** — View past chat sessions
- **Settings** — Configure JIRA connection, change password
- **Admin** (if admin) — Manage users, system settings

---

## Feature Generation (ATDD)

### How It Works

The system runs an **11-agent pipeline** that:

1. **Reads** your JIRA story or CSV input
2. **Extracts domain context** from CAS knowledge base
3. **Defines story scope** from acceptance criteria
4. **Plans test coverage** with LogicalIDs and scenarios
5. **Decomposes actions** into Given/When/Then steps
6. **Retrieves repo steps** and grounds in existing tests
7. **Composes scenarios** with behavior-descriptive titles
8. **Validates structure** against ATDD rules
9. **Writes** complete `.feature` file
10. **Reviews quality** and optionally refines
11. **Reports** final output with confidence score

### Generate from JIRA Story

**If you have a live JIRA instance:**

1. Go to **Feature Generation** → **From JIRA**
2. Enter story ID: `CAS-256008`
3. Select flow type:
   - **Unordered** — Simple happy path flows
   - **Ordered** — Complex multi-threaded flows with prerequisites
4. Add notes for the three amigos (optional)
5. Click **Generate**

**Live progress:**
- See each agent number as it completes
- Typical runtime: 2-5 minutes depending on LLM speed
- Real-time streaming shows which agent is working

### Generate from CSV

**If you have a CSV with story details:**

1. Go to **Feature Generation** → **From CSV**
2. Paste or upload CSV with columns:
   ```
   Feature, Story ID, Acceptance Criteria, Context
   Collateral Registration, CAS-256008, Verify mandatory fields..., User is authorized...
   ```
3. Select flow type (Ordered/Unordered)
4. Add notes
5. Click **Generate**

### Review Generated Output

Once complete, you'll see:

**Feature File:**
```gherkin
Feature: Collateral Registration
  As a CAS user
  I want to register new collateral
  So that I can complete the assessment

  @CAS-256008 @UnorderedFlow
  Scenario: User registers valid collateral
    Given User has login credentials
    When User enters valid collateral details
    Then System validates and stores collateral
    And System displays success message

  Scenario: System validates mandatory fields
    Given User is on collateral form
    When User omits mandatory field
    Then System shows validation error
```

**Gap Report:**
```
Coverage Gaps (5):
- Risk assessment not covered
- Document verification not tested
- Error handling for timeout scenarios

Retrieval Gaps (2):
- "Verify mandatory fields" - [LOW_MATCH] - ce_score 0.45
- "Assess collateral risk" - [NEW_STEP_NOT_IN_REPO] - ce_score 0.12
```

**Markers Legend:**
- ✅ No marker — Step found in repo with high confidence (ce_score ≥ 0.7)
- ⚠️ `[LOW_MATCH]` — Step found but low confidence (0.3 ≤ ce_score < 0.7)
- ❌ `[NEW_STEP_NOT_IN_REPO]` — Step not found in repository (ce_score < 0.3)
- ⚡ `[ROLE_GAP]` — Step conflicts with domain role graph

### Download & Use Feature File

1. Click **Download** to save `.feature` file locally
2. Copy to your test project: `features/`
3. Run with your test framework:
   ```bash
   behave features/CAS_256008.feature
   # OR
   cucumber features/CAS_256008.feature
   ```

### Quality Indicators

Each generation shows:

| Indicator | Good | Warning | Bad |
|-----------|------|---------|-----|
| **Confidence** | ≥ 0.8 | 0.5-0.8 | < 0.5 |
| **Repo Grounding** | < 20% new steps | 20-40% new steps | > 40% new steps |
| **Validation** | All rules pass | 1-2 warnings | Validation failed |
| **Coverage** | All gaps defined | Some gaps unclear | No gap analysis |
| **Ready to Commit** | ✅ Yes | ⚠️ Manual review | ❌ Needs rework |

### Ordered Flow Specifics

If generating an **ordered flow**:

```
@OrderedFlow
Scenario: CAS_256008_Initiate: User initiates collateral assessment
  Given User is logged into CAS [PREREQUISITE_FIRST]
  When User selects "Register Collateral"
  Then System loads collateral form

Scenario: CAS_256008_Validate: System validates collateral details
  # Depends on: CAS_256008_Initiate (runs after)
  Given User has filled collateral form
  When User clicks Submit
  Then System validates all mandatory fields
```

**Key rules for ordered:**
- First `Given` is the prerequisite (exact copy from `order.json`)
- No `But` keyword allowed
- No `Background` block (prerequisites explicit)
- No dictionary/examples (one flow only)
- `@Order` or `@OrderedFlow` tag required
- LogicalID in scenario name: `CAS_[StoryID]_[Intent]`

---

## CAS Assistant (Chat)

### Starting a Chat

1. Click **Chat** in navigation
2. Type your question:
   ```
   "What are the mandatory fields for collateral registration?"
   ```
3. Chat auto-detects context:
   - **CAS** — Domain knowledge injection
   - **ATDD** — Framework knowledge injection
   - **General** — Plain LLM response

### Context Types

**CAS Context** (automatic if CAS docs indexed):
- Questions about domain rules, fields, workflows
- Answered with relevant CAS document excerpts
- Example: "What is risk assessment"

**ATDD Context**:
- Questions about test structure, BDD patterns, Gherkin syntax
- Answered with framework knowledge
- Example: "What's the difference between Scenario and Scenario Outline?"

**General**:
- Other questions, off-topic
- Plain LLM response without knowledge injection
- Example: "What's the capital of France?"

### Session History

1. Click **Sessions** to see past conversations
2. Click session to view full history
3. Delete session: Click **Delete** (data cleared immediately)

### Tips for Better Answers

**Good questions:**
```
"What happens if collateral value exceeds the limit?"
"How do we validate mandatory fields in CAS?"
"What are the prerequisites for ordered flows?"
```

**Vague questions:**
```
"Tell me about CAS"  ← Too broad
"How does it work?"  ← Missing context
```

---

## Settings & Configuration

### Account Settings

1. Click **Settings** in navigation
2. Update:
   - **Display Name** — How you appear in the system
   - **Password** — Change your login password

### JIRA Configuration

If using JIRA direct mode (instead of CSV):

1. Go to **Settings** → **JIRA**
2. Enter:
   - **JIRA URL** — `https://your-jira-instance.atlassian.net`
   - **Personal Access Token (PAT)** — Generate from JIRA settings
3. Click **Test Connection** to verify
4. Once configured, can select "From JIRA" in Feature Generation

**Getting a JIRA PAT:**
1. Login to your JIRA instance
2. Click your profile → **Settings**
3. Go to **Personal Access Tokens** → **Create Token**
4. Give it a name: `Forge Agentic`
5. Grant scope: `Read Jira user data`, `Read Jira issue data`
6. Copy token and paste into Forge Settings

### Model Testing (Admin Only)

Test if LLM and vector models are responsive:

1. **Test LLM** — Runs a quick completion (5-10 seconds)
2. **Test Model** — Verifies embedding model loads

If either fails:
- LLM model file may be corrupted
- Check logs: See [How_to_Run.md](How_to_Run.md) monitoring section
- Contact admin to rebuild indices

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Submit chat message |
| `Ctrl+K` | Open command palette (future) |
| `Escape` | Close modal or dialog |
| `Ctrl+C` | Cancel running generation job |

---

## Troubleshooting

### Generation Job Stuck

**Issue:** Job shows "running" for >10 minutes

**Solution:**
1. Check logs by asking admin
2. Refresh page (job continues in background)
3. If truly hung: Admin can mark job failed in database
4. Restart = automatic cleanup of hung jobs older than 1 hour

### Can't Generate from JIRA

**Error:** "Story not found" or "Connection failed"

**Solutions:**
1. Verify JIRA URL is correct (no trailing slash): `https://...atlassian.net`
2. Check PAT is valid (doesn't expire)
3. Click **Test Connection** to verify
4. If test passes but generation fails, contact admin with story ID

### Chat Session Stuck

**Issue:** Message not sending, no response

**Solution:**
1. Refresh browser (F5)
2. Click **Sessions** and open existing session
3. If CAS assistant: Check LLM is running (`Forge health check`)
4. Try simpler question: "test"

### Can't Download Generated File

**Issue:** Download button doesn't work

**Solutions:**
1. Browser blocking: Check popup blocker settings
2. Disk space: Ensure enough space locally
3. Permissions: Check write permissions to Downloads folder
4. Fallback: Copy/paste feature file text directly

### Memory/Performance Issues

**If UI is slow:**
1. Close other browser tabs
2. Refresh page (F5)
3. Clear browser cache (`Ctrl+Shift+Del`)
4. Try different browser (Chrome, Firefox, Edge)

**If generation jobs are slow:**
- LLM model may be loading (first request is slowest)
- Feature repo may be large (FAISS search time)
- Ask admin to check system resources

---

## FAQ

### Q: Do I need internet connection?

**A:** No. Forge Agentic is fully offline:
- LLM runs locally (no cloud API)
- Feature repository indexed locally
- CAS knowledge base stored locally
- Database runs on local PostgreSQL

Internet not needed after setup.

### Q: Can I use my own feature repository?

**A:** Yes! Admin must configure `FEATURES_REPO_PATH` in `.env` and run:
```bash
python -m forge.scripts.index_repo --full-rebuild
```

Then all generation jobs will ground against your steps.

### Q: What's the "confidence" score?

**A:** Weighted average of:
- 40% — Repo grounding (% of high-match steps)
- 30% — Validation (all ATDD rules pass?)
- 20% — Coverage (gaps clearly defined?)
- 10% — Domain context (CAS certainty)

Confidence ≥ 0.8 = ready to commit
Confidence < 0.6 = needs review

### Q: Why are some steps marked `[NEW_STEP_NOT_IN_REPO]`?

**A:** Means the LLM generated a step that doesn't exist in your feature repository.

**Common reasons:**
1. Step genuinely new to your test suite
2. Repository incomplete or not indexed
3. Step phrased differently than existing step

**Action:**
1. Review: Is this a genuinely new test case?
2. If similar to existing: Edit feature file to use existing step
3. If truly new: Add to your repository for future reuse

### Q: Can I edit the generated feature file?

**A:** Absolutely! Generated files are starting points:
1. Download `.feature` file
2. Edit in your editor of choice
3. Add/remove scenarios
4. Refine step text
5. Commit to your repo

Forge doesn't lock files.

### Q: What if validation fails?

**A:** The system found ATDD rule violations. Common reasons:
1. `But` keyword used (not allowed)
2. `Then` block has >2 items (max one `Then` + one `And`)
3. `Background` in ordered flow (not allowed)
4. Missing prerequisite in ordered scenario

**Fix:**
1. Review the feature file (shown in UI)
2. Click **Refine** (if available) → Agent 7 re-composes with feedback
3. Or manually edit the file before committing

### Q: How do I use ordered flows?

**A:** Select "Ordered" flow type when generating. System will:
1. Detect prerequisites from `order.json`
2. Generate scenarios with LogicalID
3. Ensure first Given matches prerequisite exactly
4. Add `@OrderedFlow` and `@Order` tags
5. Validate all ordered rules

**Example ordered scenario:**
```gherkin
@OrderedFlow
Scenario: CAS_256008_Step1: User provides collateral details
  Given User is logged in   [← PREREQUISITE]
  When User fills form
  Then System displays confirmation

Scenario: CAS_256008_Step2: User submits collateral
  Given User has filled form  [← from step 1]
  When User clicks Submit
  Then System processes request
```

### Q: Where are my files stored?

**A:** Generation jobs are stored in:
- **Database:** PostgreSQL `agentic_forge_local`
- **FAISS Indices:** `D:\Code\Agentic_Forge\data\indices\`
- **Chat History:** PostgreSQL `chat_sessions`, `chat_messages` tables

Generated `.feature` files are NOT auto-saved (you download them).

### Q: How do I back up my data?

**A:** See [How_to_Maintain.md](How_to_Maintain.md) "Backups & Recovery" section.

Quick backup:
```bash
pg_dump -U postgres -d agentic_forge_local | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Q: Can I integrate with CI/CD?

**A:** Yes, via API. Generated files can be:
1. Downloaded and committed to git
2. Stored in artifact repository
3. Automatically run in test pipeline

See backend API docs at: `http://localhost:8000/docs`

### Q: What if I find a bug?

**A:** Report to your admin with:
1. Steps to reproduce
2. Expected vs actual behavior
3. Screenshot/feature file affected
4. Server logs (if available): `logs/forge.log`

---

## Next Steps

- **Generate your first feature file** → Feature Generation → From CSV
- **Ask a domain question** → Chat → "What is risk assessment?"
- **Review your settings** → Settings → JIRA → Test Connection
- **Explore the API** → http://localhost:8000/docs (for developers)

**Questions?** Contact your system administrator or see [How_to_Run.md](How_to_Run.md) and [How_to_Maintain.md](How_to_Maintain.md) for operational details.
