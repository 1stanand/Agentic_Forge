from typing import TypedDict, Optional, List, Dict, Any


class ForgeState(TypedDict):
    # User Input
    user_id: str
    jira_input_mode: str
    jira_story_id: Optional[str]
    jira_pat_override: Optional[str]
    jira_csv_raw: Optional[str]
    flow_type: str
    three_amigos_notes: str

    # Agent 1 — Reader
    jira_facts: Dict[str, Any]

    # Agent 2 — Domain Expert
    domain_brief: Dict[str, Any]

    # Agent 3 — Scope Definer
    scope: Dict[str, Any]

    # Agent 4 — Coverage Planner
    coverage_plan: Dict[str, Any]

    # Agent 5 — Action Decomposer
    action_sequences: List[Dict[str, Any]]

    # Agent 6 — Retriever
    retrieved_steps: Dict[str, Any]

    # Agent 7 — Composer
    composed_scenarios: List[Dict[str, Any]]

    # Agent 8 — ATDD Expert
    reviewed_scenarios: List[Dict[str, Any]]

    # Agent 9 — Writer
    feature_file: str

    # Agent 10 — Critic
    critique: Dict[str, Any]

    # Agent 11 — Reporter
    final_output: Dict[str, Any]

    # Loop-back control (Agent 10 → 07)
    is_second_pass: Optional[bool]
