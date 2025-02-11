from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.llm import ChatOpenAISingleton
from src.models import OutputTickerReport
from src.tools import TOOLS


class State(TypedDict):
    """State of the agent graph."""
    messages: Annotated[list, add_messages]

    status: str
    ticker: str
    analysis: str
    report: OutputTickerReport

def agent_analysis(state: State) -> dict:
    """Agent to analyze the stock ticker."""
    llm = ChatOpenAISingleton.get_instance()
    subgraph = create_react_agent(llm, TOOLS)

    messages = [("system", (
        "You are an AI agent specialized in finance analysis. "
        "Your job is to use tools to gather relevant data about the stock ticker "
        "and analyze it to provide a comprehensive report back to your supervisor agent. "
        'Be sure to include ticker about which the analysis is being conducted in your response. '
        '\n'
        f"Ticker: {state['ticker']}"
    ))]

    response = subgraph.invoke({"messages": messages})
    return {'analysis': response['messages'][-1].content}

def agent_report(state: State) -> dict:
    """Agent to create a report based on the analysis."""
    llm = ChatOpenAISingleton.get_instance()
    llm_structured = llm.with_structured_output(OutputTickerReport)

    if not state.get('analysis'):
        raise ValueError('Analysis is missing!')

    messages = [
        ('system', state['analysis']),
        ('system', (
            'You are an AI agent finance analysis report generation. '
            'Your job is to use the gathered data to create a comprehensive report '
            'about the stock ticker and provide it to the end human user. '
            f'The report must only be about ticket {state["ticker"]}. '
            'DO NOT MAKE UP ANY DATA. IF YOU DO NOT KNOW SOMETHING, LEAVE IT OUT. '
            'USE THE DATA YOU HAVE AVAILABLE. '
        )),
    ]
    return {'report': llm_structured.invoke(messages)}

class SupervisorOutput(BaseModel):
    """Output from the supervisor agent."""
    next_agent: str = Field(..., description='Next agent to run')
    status: str = Field(
        ...,
        description=(
            'Current status of analysis, for example "gathering data...", '
            '"getting current prices...", "getting analyst recommendations..."'
        )
    )

def supervisor(state: State) -> Command[Literal["agent_analysis", "agent_report"]]:
    """Supervisor agent to control the flow of the agents."""
    llm = ChatOpenAISingleton.get_instance()
    llm_structured = llm.with_structured_output(SupervisorOutput)

    messages = state['messages'] + [
        ('system', (
            'You are the supervisor of a financial analysis and monitoring system. '
            'Please provide the current status of the operation to update the user interface accordingly. '
            'Based on the previous conversation, determine the next appropriate action. '
            'Here are the possible actions you can take:\n'
            'agent_analysis: Conduct a thorough analysis of the stock ticker and generate a detailed report.\n'
            'agent_report: Create a report based on the analysis and deliver it to the user.'
            f'State:\n'
            f'Analysis conducted: {bool(state.get('analysis'))}'
        )),
    ]
    response: SupervisorOutput = SupervisorOutput.parse_obj(llm_structured.invoke(messages))

    print("Supervisor response:", response)
    return Command(
        goto=response.next_agent,
        update={
            'status': response.status
        }
    )


builder = StateGraph(State)
builder.add_node(supervisor)
builder.add_node(agent_analysis)
builder.add_node(agent_report)

builder.set_entry_point("supervisor")
builder.add_edge("agent_analysis", "supervisor")
builder.add_edge("agent_report", END)

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
