"""Graph definition module.

This module contains the graph definition for the agent.
Resources:
    - https://langchain-ai.github.io/langgraph/concepts/low_level/#graphs
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents import agent_analysis, agent_report, supervisor
from src.state import State


def build_compiled_graph() -> CompiledStateGraph:
    """Build the compiled state graph for the agent.

    Returns:
        CompiledStateGraph: Compiled graph.
    """
    builder = StateGraph(State)
    builder.add_node(supervisor)
    builder.add_node(agent_analysis)
    builder.add_node(agent_report)

    builder.set_entry_point('supervisor')
    builder.add_edge('agent_analysis', 'supervisor')
    builder.add_edge('agent_report', END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)
