import os

from apify import Actor
from langchain_core.messages import ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.prebuilt import create_react_agent
from src.llm import ChatOpenAISingleton

from src.models import OutputTickerReport
from src.tools import TOOLS, tool_get_ticker_info, tool_get_ticker_news, tool_get_ticket_price_targets


async def main() -> None:
    """Actor entry point."""
    async with Actor:
        actor_input = await Actor.get_input()
        ticker = actor_input.get('ticker')
        openai_api_key = actor_input.get('openai_api_key')
        model = actor_input.get('model')
        if not ticker:
            msg = 'Missing "ticker" attribute in input!'
            raise ValueError(msg)
        if not openai_api_key:
            msg = 'Missing "openai_api_key" attribute in input!'
            raise ValueError(msg)
        os.environ['OPENAI_API_KEY'] = openai_api_key
        llm = ChatOpenAISingleton.create_get_instance(model=model)

        #from src.graph import graph
        #config: RunnableConfig = {"configurable": {"thread_id": "1"}}
        #graph.update_state(config, {'ticker': ticker})

        tools = TOOLS
        graph = create_react_agent(llm, tools, response_format=OutputTickerReport)

        #messages = [
        #]

        messages = [
            ('system', (
                'You are an AI agent specialized in finance analysis. '
                'The user will provide a stock ticker, and your task is to gather relevant data including news, '
                'analyst target prices, analyst recommendations, and recent stock prices. '
                'After collecting the data, analyze it and provide a comprehensive report back to the user. '
                'The report should include a summary of important news and an analysis '
                'of what to expect from the stock ticker.'
            )),
            ('user', f'Please analyze the stock ticker {ticker}.')
        ]
        inputs = {'messages': messages}
        #for s in graph.stream(inputs, config, stream_mode='values'):
        for s in graph.stream(inputs, stream_mode='values'):
            #print('------------------------')
            #print(s)
            #continue
            message = s['messages'][-1]
            print('------------------------')
            print(s.keys())
            print(len(s['messages']), [type(m) for m in s['messages']])
            if isinstance(message, ToolMessage):
                continue
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

            if 'structured_response' in s:
                print('Structured response:')
                print(s['structured_response'])
            else:
                print('No structured response')
