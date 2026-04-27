"""
Chat Message Router

Classifies incoming chat messages into context types:
- cas: CAS domain-specific questions (retriever context)
- atdd: ATDD framework questions (CAS_ATDD_Context knowledge)
- general: Generic conversation (no special context)
"""

import logging
from typing import Literal

from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are a message router for Forge Agentic Chat.

Your job: Classify user messages into one of three context types.

## Context Types

1. **cas** — CAS domain-specific questions
   - Examples: "What are mandatory fields for Collateral?", "What screens are in Credit Approval?"
   - Trigger: mentions screens, stages, LOBs, business rules, domain concepts
   - Handler: RAG engine fetches CAS documentation

2. **atdd** — ATDD framework and methodology questions
   - Examples: "What is a LogicalID?", "How do I write ordered flows?", "What is marker [LOW_MATCH]?"
   - Trigger: mentions ATDD, Gherkin, BDD, scenarios, features, flow types, markers
   - Handler: Inject CAS_ATDD_Context.md content

3. **general** — Generic conversation
   - Examples: "Hello", "How are you?", "Tell me about yourself"
   - Trigger: no domain or ATDD keywords
   - Handler: Plain LLM response, no special context

## Output

Respond with JSON only:
{
  "context_type": "cas | atdd | general",
  "confidence": 0.0 to 1.0,
  "reasoning": "Why this classification"
}
"""

def classify_message(message: str) -> Literal["cas", "atdd", "general"]:
    """Classify message into cas, atdd, or general context type."""

    logger.debug(f"Classifying: {message[:100]}...")

    # Quick keyword heuristic before LLM (fast path)
    message_lower = message.lower()

    # ATDD keywords
    atdd_keywords = ["logicalid", "ordered flow", "gherkin", "bdd", "scenario", "feature",
                     "marker", "new_step", "low_match", "role_gap", "background",
                     "given/when/then", "acceptance criteria", "atdd", "behavior"]
    if any(kw in message_lower for kw in atdd_keywords):
        logger.debug("Quick match: ATDD keywords detected")
        return "atdd"

    # CAS domain keywords
    cas_keywords = ["collateral", "credit approval", "applicant", "guarantor", "lob",
                    "stage", "screen", "mandatory field", "business rule", "cas",
                    "approval process", "document verification", "sanction list",
                    "rating", "pricing", "risk", "workflow", "entity", "exposure"]
    if any(kw in message_lower for kw in cas_keywords):
        logger.debug("Quick match: CAS keywords detected")
        return "cas"

    # If quick match failed, use LLM
    logger.debug("Quick match inconclusive, calling LLM classifier")

    try:
        llm_input = f"""Classify this message:

"{message}"

Respond with JSON only. Choose ONE context type: cas, atdd, or general.
"""
        response = llm_complete(
            prompt=llm_input,
            system=ROUTER_SYSTEM_PROMPT,
            max_tokens=200
        )

        # Parse JSON response
        import json
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            result = json.loads(json_str)
            context_type = result.get("context_type", "general").lower()

            if context_type not in ["cas", "atdd", "general"]:
                logger.warning(f"Invalid context type: {context_type}, defaulting to general")
                context_type = "general"

            logger.debug(f"LLM classified as: {context_type} (confidence={result.get('confidence')})")
            return context_type

        except Exception as e:
            logger.warning(f"JSON parse error in router: {e}, defaulting to general")
            return "general"

    except LLMNotLoadedError:
        logger.warning("LLM not loaded, defaulting to general context")
        return "general"

    except Exception as e:
        logger.error(f"Router error: {e}, defaulting to general")
        return "general"
