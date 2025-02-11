from langgraph.graph.state import CompiledStateGraph

from src.graph import build_compiled_graph


def test_build_compiled_graph() -> None:
    """Test if the graph is built without errors."""
    graph = build_compiled_graph()
    assert isinstance(graph, CompiledStateGraph)
