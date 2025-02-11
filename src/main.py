import logging
import os
from typing import TYPE_CHECKING

from apify import Actor

from src.graph import build_compiled_graph
from src.llm import ChatOpenAISingleton

if TYPE_CHECKING:
    from langchain_core.runnables.config import RunnableConfig

    from src.models import OutputTickerReport

logger = logging.getLogger('apify')


async def main() -> None:
    """Actor entry point.

    Raises:
        ValueError: If required attributes
    """
    async with Actor:
        # Handle input
        actor_input = await Actor.get_input()
        ticker = actor_input.get('ticker')
        openai_api_key = actor_input.get('openai_api_key')
        model = actor_input.get('model')
        debug = actor_input.get('debug', False)
        if debug:
            logger.setLevel(logging.DEBUG)
        if not ticker:
            msg = 'Missing "ticker" attribute in input!'
            raise ValueError(msg)
        if not openai_api_key:
            msg = 'Missing "openai_api_key" attribute in input!'
            raise ValueError(msg)
        os.environ['OPENAI_API_KEY'] = openai_api_key
        # Create ChatOpenAI singleton instance
        ChatOpenAISingleton.create_get_instance(model=model)

        # Create the graph
        config: RunnableConfig = {'configurable': {'thread_id': '1', 'debug': debug}}
        graph = build_compiled_graph()
        graph.update_state(config, {'ticker': ticker})

        # Run the graph
        inputs: dict = {'messages': []}
        report: OutputTickerReport | None = None
        actor_status = None
        async for state in graph.astream(inputs, config, stream_mode='values'):
            logger.debug('-------- State --------')
            logger.debug('State: %s', state)
            status = state.get('status')
            if status and status != actor_status:
                await Actor.set_status_message(f'Agent: {status}')
                logger.info('Agent: %s', status)
                actor_status = status

            if report := state.get('report'):
                break

        if not report:
            msg = 'Failed to generate the report!'
            raise ValueError(msg)

        logger.info('-------- Report --------')
        logger.info('Report: %s', report)

        await Actor.push_data(
            {
                'ticker': report.ticker,
                'sentiment': report.sentiment,
                'sentiment_reason': report.sentiment_reason,
                'report': report.report,
            }
        )
