import datetime
import logging
from typing import Literal

from langchain_core.runnables.config import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from src.llm import ChatOpenAISingleton
from src.models import OutputTickerReport, SupervisorOutput
from src.state import State
from src.tools import (
    tool_get_ticker_info,
    tool_get_ticker_news,
    tool_get_ticker_recommendations,
    tool_get_ticket_price_targets,
)

logger = logging.getLogger('apify')


async def agent_analysis(state: State, config: RunnableConfig) -> dict:
    """Agent to analyze the stock ticker.

    Returns:
        dict: graph state update with the analysis.
    """
    llm = ChatOpenAISingleton.get_instance()
    tools = [
        tool_get_ticker_info,
        tool_get_ticker_news,
        tool_get_ticket_price_targets,
        tool_get_ticker_recommendations,
    ]
    subgraph = create_react_agent(llm, tools)

    messages = [
        (
            'system',
            (
                'You are an AI agent specialized for finance data gathering and summarization. '
                'Your job is to use tools to gather relevant data about the stock ticker '
                'and summarize it. Be sure to include important information and events, '
                'analyst reccomendations and price targets.'
                '\n'
                f'Ticker: {state["ticker"]}'
                f"Today's date: {datetime.datetime.now(tz=datetime.UTC).strftime('%Y-%m-%d')}"
            ),
        )
    ]

    debug = config.get('configurable', {}).get('debug', False)
    if debug:
        response: dict = {}
        async for substate in subgraph.astream({'messages': messages}, stream_mode='values'):
            message = substate['messages'][-1]
            logger.debug('-------- Analyst --------')
            logger.debug('Message: %s', message)
            response = substate
    else:
        response = await subgraph.ainvoke({'messages': messages})

    return {'analysis': response['messages'][-1].content}


def agent_report(state: State) -> dict:
    """Agent to create a report based on the analysis.

    Returns:
        dict: graph state update with the report.

    Raises:
        ValueError: If analysis is missing.
    """
    llm = ChatOpenAISingleton.get_instance()
    llm_structured = llm.with_structured_output(OutputTickerReport)

    if not state.get('analysis'):
        msg = 'Analysis is missing!'
        raise ValueError(msg)

    messages = [
        (
            'system',
            (
                'You are an AI agent for finance report generation. '
                'Create a comprehensive report about the stock ticker using the provided data. '
                'DO NOT MAKE UP ANY DATA. IF YOU DO NOT KNOW SOMETHING, LEAVE IT OUT. '
                'DO NOT TRY TO INTERACT WITH THE USER, ONLY CREATE A REPORT. '
                'REPORT OUTLINE MUST BE AS FOLLOWS (MD format):\n'
                '- Executive summary - brief overview of the company news from the analysis and its financial health.\n'
                '- Important events - recent news and events that may have affected the stock price.\n'
                '- Stock price - current stock price and price targets.\n'
                '- Analyst recommendations - current analyst recommendations for the stock.\n'
                '- Conclusion - final thoughts on the stock and its future prospects.\n'
                f'Ticker: {state["ticker"]}'
                f"Today's date: {datetime.datetime.now(tz=datetime.UTC).strftime('%Y-%m-%d')}"
            ),
        ),
        ('assistant', f'Here the ticker news and analysis:\n{state["analysis"]}'),
    ]
    return {'report': llm_structured.invoke(messages)}


def supervisor(state: State) -> Command[Literal['agent_analysis', 'agent_report']]:
    """Supervisor agent to control the flow of the agents.

    Returns:
        Command: Command with status update and goto next agent.
    """
    llm = ChatOpenAISingleton.get_instance()
    llm_structured = llm.with_structured_output(SupervisorOutput)

    messages = [
        (
            'system',
            (
                'You are the supervisor of a financial analysis and monitoring system. '
                'Please provide the current status of the operation to update the user interface accordingly. '
                'Based on the current state, determine the next appropriate action. '
                'Here are the possible actions you can take:\n'
                'agent_analysis: Conduct a thorough analysis of the stock ticker and generate a detailed report.\n'
                'agent_report: Create a report based on the analysis and deliver it to the user.\n'
                f'State:\n'
                f'Analysis conducted: {bool(state.get("analysis"))}'
            ),
        ),
    ]
    response: SupervisorOutput = SupervisorOutput.parse_obj(llm_structured.invoke(messages))

    logger.debug('Supervisor response: %s', response)
    return Command(goto=response.next_agent, update={'status': response.status})
