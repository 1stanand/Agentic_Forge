import logging
from langgraph.graph import StateGraph, END

from forge.core.state import ForgeState
from forge.agents.agent_01_reader import agent_01_reader
from forge.agents.agent_02_domain_expert import agent_02_domain_expert
from forge.agents.agent_03_scope_definer import agent_03_scope_definer
from forge.agents.agent_04_coverage_planner import agent_04_coverage_planner
from forge.agents.agent_05_action_decomposer import agent_05_action_decomposer
from forge.agents.agent_06_retriever import agent_06_retriever
from forge.agents.agent_07_composer import agent_07_composer
from forge.agents.agent_08_atdd_expert import agent_08_atdd_expert
from forge.agents.agent_09_writer import agent_09_writer
from forge.agents.agent_10_critic import agent_10_critic
from forge.agents.agent_11_reporter import agent_11_reporter

logger = logging.getLogger(__name__)


def _critic_loop_back_edge(state: ForgeState) -> str:
    """Conditional edge after Critic: loop back to Composer or proceed to Reporter.

    Enforces hard rule: maximum one loop via is_second_pass flag.
    """
    critic_review = state.critic_review or {}
    is_second_pass = state.is_second_pass if hasattr(state, 'is_second_pass') else False

    loop_back = critic_review.get("loop_back", False)

    if loop_back and not is_second_pass:
        logger.info("Critic: Loop back to Composer (first pass)")
        # Mark state for second pass to prevent further loops
        state.is_second_pass = True
        return "agent_07"
    else:
        if is_second_pass:
            logger.info("Critic: Second pass detected, hard-stopping loop")
        else:
            logger.info("Critic: Proceeding to Reporter")
        return "agent_11"


# Build the graph
def build_graph():
    graph = StateGraph(ForgeState)

    # Add all nodes
    graph.add_node("agent_01", agent_01_reader)
    graph.add_node("agent_02", agent_02_domain_expert)
    graph.add_node("agent_03", agent_03_scope_definer)
    graph.add_node("agent_04", agent_04_coverage_planner)
    graph.add_node("agent_05", agent_05_action_decomposer)
    graph.add_node("agent_06", agent_06_retriever)
    graph.add_node("agent_07", agent_07_composer)
    graph.add_node("agent_08", agent_08_atdd_expert)
    graph.add_node("agent_09", agent_09_writer)
    graph.add_node("agent_10", agent_10_critic)
    graph.add_node("agent_11", agent_11_reporter)

    # Wire edges in sequence (1 → 2 → 3 → ... → 9 → 10)
    graph.add_edge("agent_01", "agent_02")
    graph.add_edge("agent_02", "agent_03")
    graph.add_edge("agent_03", "agent_04")
    graph.add_edge("agent_04", "agent_05")
    graph.add_edge("agent_05", "agent_06")
    graph.add_edge("agent_06", "agent_07")
    graph.add_edge("agent_07", "agent_08")
    graph.add_edge("agent_08", "agent_09")
    graph.add_edge("agent_09", "agent_10")

    # Conditional edge from Critic (10) → Composer (7) or Reporter (11)
    # Enforces: max 1 loop via is_second_pass flag
    graph.add_conditional_edges(
        "agent_10",
        _critic_loop_back_edge,
        {
            "agent_07": "agent_07",
            "agent_11": "agent_11"
        }
    )

    # If looping back, Composer → ATDD Expert (skip 06 Retriever, reuse retrieved_steps)
    graph.add_edge("agent_07", "agent_08")

    # Set entry and finish points
    graph.set_entry_point("agent_01")
    graph.set_finish_point("agent_11")

    return graph.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_graph(state: ForgeState) -> ForgeState:
    graph = get_graph()
    result = graph.invoke(state)
    return result
