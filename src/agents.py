import datetime
import logging
from typing import Literal

from langchain_core.messages import ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from src.llm import ChatOpenAISingleton
from src.models import OutputTickerReport
from src.state import State
from src.tools import (
    tool_get_google_news,
    tool_get_ticker_basic_info,
    tool_get_ticker_price_targets,
    tool_get_ticker_recommendations,
    tool_get_yahoo_ticker_news,
)

logger = logging.getLogger('apify')


async def agent_analysis(state: State, config: RunnableConfig) -> dict:
    """Agent to analyze the stock ticker.

    This agent uses tools to gather relevant data about the stock ticker and summarize it.
    The summary is then passed to the next agent.

    Returns:
        dict: graph state update with the analysis.
    """
    llm = ChatOpenAISingleton.get_instance()
    tools = [
        tool_get_ticker_basic_info,
        tool_get_yahoo_ticker_news,
        tool_get_ticker_price_targets,
        tool_get_ticker_recommendations,
        tool_get_google_news,
    ]
    subgraph = create_react_agent(llm, tools)

    messages = [
        (
            'user',
            (
                'You are an AI agent specialized for finance data gathering and summarization. '
                'Your job is to use tools to gather relevant data about the stock ticker '
                'and summarize it. Be sure to include important information and events, '
                'analyst recommendations and price targets. '
                'Gather information from as many sources as you have access to. '
                'So if you have tools available for news from Yahoo, Google and X.com, use all of them. '
                'If you have source link available, include it in the summary. '
                'If for some reason any tool fails, try to rerun it once more.'
                '\n'
                f'Ticker: {state["ticker"]}\n'
                f"Today's date: {datetime.datetime.now(tz=datetime.UTC).strftime('%Y-%m-%d')}"
            ),
        )
    ]

    debug = config.get('configurable', {}).get('debug', False)
    if debug:
        response: dict = {}
        async for substate in subgraph.astream({'messages': messages}, stream_mode='values'):
            message = substate['messages'][-1]
            # traverse all tool messages and print them
            if isinstance(message, ToolMessage):
                # until the analyst message with tool_calls
                for _message in substate['messages'][::-1]:
                    if hasattr(_message, 'tool_calls'):
                        break
                    logger.debug('-------- Tool --------')
                    logger.debug('Message: %s', _message)
                continue

            logger.debug('-------- Analyst --------')
            logger.debug('Message: %s', message)
            response = substate
    else:
        response = await subgraph.ainvoke({'messages': messages})

    return {'analysis': response['messages'][-1].content}


def agent_report(state: State) -> dict:
    """Agent to create a report based on the analysis.

    This agent generates a report about the stock ticker using the ticker data summary.

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
            'user',
            (
                'You are an AI agent for finance report generation. '
                'Create a comprehensive report about the stock ticker using the provided data. '
                'If you have source link available for news, include it in the report. '
                'DO NOT MAKE UP ANY DATA. IF YOU DO NOT KNOW SOMETHING, LEAVE IT OUT. '
                'DO NOT TRY TO INTERACT WITH THE USER, ONLY CREATE A REPORT. '
                'REPORT OUTLINE MUST BE AS FOLLOWS (MD format):\n'
                '- Executive summary - brief overview of the company news from the analysis and its financial health.\n'
                '- Important events - recent news and events that may have affected the stock price.\n'
                '- Stock price - current stock price and price targets.\n'
                '- Analyst recommendations - current analyst recommendations for the stock.\n'
                '- Conclusion - final thoughts on the stock and its future prospects.\n'
                f'Ticker: {state["ticker"]}\n'
                f"Today's date: {datetime.datetime.now(tz=datetime.UTC).strftime('%Y-%m-%d')}"
            ),
        ),
        ('user', f'Here the ticker news and analysis:\n{state["analysis"]}'),
    ]
    return {'report': llm_structured.invoke(messages)}


# this can be an agent if the graph gets more complex
def supervisor(state: State) -> Command[Literal['agent_analysis', 'agent_report']]:
    """Supervisor node to control the flow of the agents.

    This node supervises the agents and determines the next appropriate action based on the current state and
    updates the state accordingly the user.

    Returns:
        Command: Command with status update and goto next agent.
    """
    analysis_done = bool(state.get('analysis'))

    if not analysis_done:
        status = 'gathering and analyzing data...'
        next_agent = 'agent_analysis'
    else:
        status = 'creating report...'
        next_agent = 'agent_report'

    return Command(goto=next_agent, update={'status': status})
