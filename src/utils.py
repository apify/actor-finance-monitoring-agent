from apify import Actor


async def run_actor_get_default_dataset(actor_id: str, run_input: dict) -> tuple[str, list[dict]]:
    """Run an Actor and get the default dataset.

    Args:
        actor_id (str): Actor ID.
        run_input (dict): Actor run input.

    Returns:
        str, list[dict]: Dataset ID and dataset items.

    Raises:
        RuntimeError: If Actor run fails.
    """
    if not (run := await Actor.apify_client.actor(actor_id).call(run_input=run_input)):
        msg = f'Failed to start the Actor {actor_id}!'
        raise RuntimeError(msg)

    dataset_id = run['defaultDatasetId']
    dataset_items: list[dict] = (await Actor.apify_client.dataset(dataset_id).list_items()).items
    return dataset_id, dataset_items


async def get_yahoo_dataset_data(dataset_id: str) -> dict:
    """Retrieve data from Yahoo Actor run Apify dataset.

    Args:
        dataset_id (str): Dataset ID.

    Returns:
        dict: Dataset record with the data.

    Raises:
        RuntimeError: If dataset retrieval fails.
        ValueError: If dataset is empty.
    """
    dataset_items: list[dict] = (await Actor.apify_client.dataset(dataset_id).list_items()).items
    if not dataset_items:
        msg = f'Failed to get dataset "{dataset_id}"!'
        raise RuntimeError(msg)

    if len(dataset_items) == 0:
        msg = f'Failed to get data from dataset "{dataset_id}", no items found!'
        raise ValueError(msg)

    return dataset_items[0]
