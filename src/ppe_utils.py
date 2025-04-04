"""This module contains utility functions for the PPE (Pay Per Event) usage."""

from decimal import ROUND_CEILING, Decimal

from apify import Actor
from langchain_core.messages import AIMessage, BaseMessage

MODEL_PPE_EVENT = {
    'gpt-4o': 'openai-100-tokens-gpt-4o',
    'gpt-4o-mini': 'openai-100-tokens-gpt-4o-mini',
    'o1': 'openai-100-tokens-o1',
    'o3-mini': 'openai-100-tokens-o3-mini',
}


def get_all_messages_total_tokens(messages: list[BaseMessage]) -> int:
    """Calculates the total number of tokens used in a list of messages.

    Args:
        messages (list[BaseMessage]): List of messages.

    Returns:
        int: Total number of tokens.

    Raises:
        ValueError: If a message does not have a "token_usage.total_tokens" field.
    """
    sum_tokens = 0
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        if not (tokens := message.response_metadata.get('token_usage', {}).get('total_tokens')):
            msg = f'Missing "token_usage.total_tokens" in response metadata: {message.response_metadata}'
            raise ValueError(msg)
        sum_tokens += tokens
    return sum_tokens


async def charge_for_model_tokens(model_name: str, tokens: int) -> None:
    """Charges for the tokens used by a specific model.

    Args:
        model_name (str): Model name.
        tokens (int): Number of tokens.

    Raises:
        ValueError: If the model name is unknown.
    """
    tokens_hundreds = int((Decimal(tokens) / Decimal('1e2')).to_integral_value(rounding=ROUND_CEILING))
    Actor.log.debug(f'Charging for {tokens} tokens ({tokens_hundreds} hundreds) for model {model_name}')
    if not (event_name := MODEL_PPE_EVENT.get(model_name)):
        msg = f'Unknown model name: {model_name}'
        raise ValueError(msg)
    await Actor.charge(event_name=event_name, count=tokens_hundreds)


async def charge_for_actor_start() -> None:
    """Charges for the Actor start event."""
    count = (Actor.get_env()['memory_mbytes'] or 1024 + 1023) // 1024
    await Actor.charge(event_name='actor-start-gb', count=count)
