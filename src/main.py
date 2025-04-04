import logging
from typing import TYPE_CHECKING

from apify import Actor
from langchain_community.callbacks import get_openai_callback

from src.graph import build_compiled_graph
from src.llm import ChatOpenAISingleton
from src.ppe_utils import charge_for_actor_start, charge_for_model_tokens

if TYPE_CHECKING:
    from langchain_core.runnables.config import RunnableConfig

    from src.models import OutputTickerReport

logger = logging.getLogger('apify')


async def main() -> None:
    """Actor entry point.

    Raises:
        ValueError: If required input attributes are missing
    """
    async with Actor:
        # Handle input
        actor_input = await Actor.get_input()
        ticker = actor_input.get('ticker')
        model = actor_input.get('model', 'gpt-4o-mini')  # Default model if not provided
        debug = actor_input.get('debug', False)
        if debug:
            logger.setLevel(logging.DEBUG)
        if not ticker:
            msg = 'Missing "ticker" attribute in input!'
            raise ValueError(msg)

        # Charge for actor start
        await charge_for_actor_start()

        # Create ChatOpenAI singleton instance
        ChatOpenAISingleton.create_get_instance(model=model)

        # Create the graph
        config: RunnableConfig = {'configurable': {'thread_id': '1', 'debug': debug}}
        graph = build_compiled_graph()
        graph.update_state(config, {'ticker': ticker})

        # Run the graph and track token usage
        inputs: dict = {'messages': []}
        report: OutputTickerReport | None = None
        actor_status = None
        total_tokens = 0
        with get_openai_callback() as callback:
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

        # Charge for total token usage
        total_tokens = callback.total_tokens
        await charge_for_model_tokens(model, total_tokens)

        # Add report disclaimer
        output_report = (
            f'{report.report}'
            '\n\n\n---\n\n\nThis report is generated by an AI agent and should not be considered as financial advice.\n'
        )

        store = await Actor.open_key_value_store()
        await store.set_value('report.md', output_report)
        logger.info('Saved the "report.md" file into the key-value store!')

        await Actor.push_data(
            {
                'ticker': report.ticker,
                'sentiment': report.sentiment,
                'sentiment_reason': report.sentiment_reason,
                'report': output_report,
            }
        )
        logger.info('Pushed the report to the dataset!')
