import asyncio
from collections.abc import Coroutine
from typing import Any

from apify import Actor


def run_async(func: Coroutine) -> Any:  # noqa: ANN401
    """Helper function to run async functions in a synchronous context.

    Args:
        func (Coroutine): Async function to run.

    Returns:
        Any: Result of the async function
    """
    return asyncio.run(func)

async def get_yahoo_dataset_data(dataset_id: str) -> dict:
    """Retrieve dataset from Apify.

    Args:
        dataset_id (str): Dataset ID.

    Returns:
        dict: Dataset record.

    Raises:
        RuntimeError: If dataset retrieval fails.
    """
    if not (dataset_items := (await Actor.apify_client.dataset(dataset_id).list_items()).items):
        msg = f'Failed to get dataset "{dataset_id}"!'
        raise RuntimeError(msg)

    if len(dataset_items) == 0:
        msg = f'Failed to get data from dataset "{dataset_id}", no items found!'
        raise ValueError(msg)

    return dataset_items[0]
