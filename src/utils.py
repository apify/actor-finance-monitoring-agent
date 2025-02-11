from apify import Actor


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
