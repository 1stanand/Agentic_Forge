"""
Chat Engine

Conversation loop with context-aware responses.
- Routes messages by context type (cas/atdd/general)
- Injects RAG context for cas questions
- Injects ATDD context for atdd questions
- Persists history via session_store
"""

import logging
from typing import Dict, Any, Optional

from forge.chat.router import classify_message
from forge.chat.session_store import (
    create_session, save_message, load_session, list_sessions, delete_session
)
from forge.core.llm import llm_complete, LLMNotLoadedError
from forge.infrastructure.rag_engine import get_context

logger = logging.getLogger(__name__)

# CAS ATDD Context — injected for atdd messages
CAS_ATDD_CONTEXT = """# CAS ATDD Framework

## Core Concepts

**LogicalID** — Unique scenario identifier: CAS_{storyID}_{intent}
- Example: CAS_256008_APPROVE
- Used for traceability and test orchestration

**Ordered Flows** — Stateful, chained scenarios with explicit dependencies
- Prerequisite: first Given step is exact step text from previous scenario
- LogicalID required in scenario title
- No dictionaries, no Background block
- Validated against order.json expressions
- Example: "CAS_256008_APPROVE : User approves application and system records decision"

**Unordered Flows** — Independent scenarios, no cross-scenario dependencies
- Optional Background block for shared Given steps
- Scenario titles are behavior-descriptive only (not structure names)
- No prerequisite constraints
- Example: "User successfully approves application"

**Markers** — Step quality indicators
- [NEW_STEP_NOT_IN_REPO] — No matching step in feature repo (ce_score < 0.3)
- [LOW_MATCH] — Weak match to repo step (0.3 ≤ ce_score < 0.7)
- [ROLE_GAP] — Step role does not match domain requirements
- Markers travel intact through pipeline; never silently dropped

## Hard Rules (Never Violate)

1. **No "But" keyword** — Ever. Restructure if needed.
2. **Then max 2 items** — One Then + one And maximum. No "And And".
3. **No dictionaries in ordered flows** — All data in step parameters only.
4. **No Background in ordered flows** — Each scenario fully self-contained.
5. **First Given = prerequisite step exact text** — Do NOT paraphrase.
6. **Markers preserved** — Never drop quality markers.

## Example Scenarios

### Ordered Flow (Stateful)
```gherkin
@CAS-256008
@OrderedFlow
Feature: Approve credit application

  Scenario: CAS_256008_APPROVE : User approves application and system records decision
    @LogicalID:CAS_256008_APPROVE
    Given user is on Credit Approval screen
    And user has selected applicant record
    When user clicks Approve button
    And user confirms decision
    Then system displays approval confirmation
    And approval decision is recorded in database
```

### Unordered Flow (Independent)
```gherkin
@CAS-256012
@UnorderedFlow
Feature: Validate collateral documents

  Background:
    Given user has completed login
    And user is in Credit Approval stage

  Scenario: User successfully uploads required document
    When user uploads collateral document
    Then system validates document format
    And system stores document in database

  Scenario: System rejects invalid document format
    When user uploads corrupted document
    Then system displays error message
    And user can re-upload document
```

## When to Use Each Flow Type

**Ordered:**
- Process flows with strict sequencing (Application → Approval → Recording)
- Loan approval workflows with state transitions
- Multi-stage processes with explicit stage gates
- Any flow where one scenario's output feeds next scenario's input

**Unordered:**
- Feature testing (feature works in isolation, no dependencies)
- Validation rules (each validation independent)
- UI feature tests (button clicks, form submissions)
- Non-process features

## CAS Vocabulary

Use these verbs in steps (matched against repo):
- Click, Select, Enter, Navigate, Verify, Validate, Approve, Reject, Submit
- Example: "Given user clicks Edit button"
- Example: "When system displays recommendation screen"
- Example: "Then user can proceed to next stage"
"""

def process_message(
    user_id: str,
    message_text: str,
    session_id: Optional[str] = None,
    screen: Optional[str] = None,
    stage: Optional[str] = None,
    lob: Optional[str] = None
) -> Dict[str, Any]:
    """Process a chat message and return response with context.

    Args:
        user_id: User making the request
        message_text: Chat message
        session_id: Existing session or None for new
        screen: CAS screen (for cas context)
        stage: CAS stage (for cas context)
        lob: CAS LOB (for cas context)

    Returns: {
        "session_id": str,
        "message_id": str,
        "context_type": "cas|atdd|general",
        "response": str,
        "context_used": bool
    }
    """

    logger.info(f"Processing message from user {user_id}")

    # Create or load session
    if not session_id:
        session_id = create_session(user_id)
        logger.debug(f"Created new session: {session_id}")
    else:
        session = load_session(session_id, user_id)  # Validates access
        logger.debug(f"Loaded existing session: {session_id}")

    # Classify message
    context_type = classify_message(message_text)
    logger.info(f"Classified as: {context_type}")

    # Build context based on type
    context_prompt = ""
    context_used = False

    if context_type == "cas":
        try:
            # Fetch CAS domain knowledge via RAG
            cas_context = get_context(
                screen=screen or "General",
                stage=stage or "General",
                lob=lob or "General",
                query=message_text
            )
            if cas_context:
                context_prompt = f"\n\nCAS Domain Context:\n{cas_context}"
                context_used = True
                logger.debug(f"CAS context fetched: {len(cas_context)} chars")
        except Exception as e:
            logger.warning(f"CAS context fetch failed: {e}")
            # Continue without context

    elif context_type == "atdd":
        # Inject ATDD framework knowledge
        context_prompt = f"\n\n{CAS_ATDD_CONTEXT}"
        context_used = True
        logger.debug("ATDD context injected")

    # Generate response
    try:
        system_prompt = _build_system_prompt(context_type)

        llm_input = f"""User message: {message_text}{context_prompt}

Provide a helpful, concise response. If context was provided, use it to answer accurately.
Keep response under 500 chars."""

        response = llm_complete(
            prompt=llm_input,
            system=system_prompt,
            max_tokens=300
        )

        logger.debug(f"LLM response: {len(response)} chars")

    except LLMNotLoadedError:
        logger.warning("LLM not loaded, providing fallback response")
        response = (
            "I'm unable to generate a response right now (LLM not loaded). "
            "Please try again in a moment or check the server logs."
        )
    except Exception as e:
        logger.error(f"LLM error: {e}")
        response = f"Error processing message: {e}"

    # Save messages to session
    user_msg_id = save_message(session_id, user_id, message_text, "user", context_type)
    asst_msg_id = save_message(session_id, user_id, response, "assistant", context_type)

    logger.info(f"Session {session_id}: messages saved")

    return {
        "session_id": session_id,
        "message_id": asst_msg_id,
        "context_type": context_type,
        "response": response,
        "context_used": context_used
    }


def _build_system_prompt(context_type: str) -> str:
    """Build system prompt based on context type."""

    if context_type == "cas":
        return """You are a CAS domain expert assistant for Nucleus Software QA team.
Your knowledge domain: CAS (Core Application System) — legacy financial system for loan/credit management.
You know: screens, stages, LOBs (Lines of Business), business rules, entities, workflows.
Answer questions about CAS domain knowledge, features, and processes.
Be accurate and cite business rules when relevant."""

    elif context_type == "atdd":
        return """You are an ATDD (Acceptance Test-Driven Development) expert for CAS.
Your knowledge: Gherkin syntax, BDD principles, ordered vs unordered flows, LogicalIDs, markers.
You guide users on: writing feature files, scenario structure, CAS conventions, quality gates.
Be prescriptive about CAS rules (no But, Then max 2, ordered flow prerequisites, etc.).
Always prefer concrete examples."""

    else:  # general
        return """You are a helpful assistant for the Forge Agentic platform.
Forge is an AI system for generating acceptance test feature files from JIRA stories.
Be friendly, concise, and helpful. If asked about CAS or ATDD specifics, you can provide general guidance."""


def get_session_history(user_id: str, session_id: str) -> Dict[str, Any]:
    """Load full session history for the user."""
    return load_session(session_id, user_id)


def list_user_sessions(user_id: str) -> list:
    """List all sessions for a user."""
    return list_sessions(user_id)


def delete_user_session(user_id: str, session_id: str) -> bool:
    """Delete a user's session."""
    return delete_session(session_id, user_id)
