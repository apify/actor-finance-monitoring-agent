"""Graph state module.

This module contains the state definition for the agent graph.
Resources:
    - https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    - https://langchain-ai.github.io/langgraph/concepts/memory/
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from src.models import OutputTickerReport


class State(TypedDict):
    """State of the agent graph."""

    messages: Annotated[list, add_messages]

    status: str
    """Current status message of the Actor to be displayed."""
    ticker: str
    """Ticker that is being analyzed."""
    analysis: str
    """Analysis and data about the ticker news, prices and recommendations."""
    report: OutputTickerReport
    """Final report for the ticker for the user."""
