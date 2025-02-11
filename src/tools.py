import logging

from apify import Actor
from langchain_core.tools import tool

from src.models import TickerInfo, TickerNewsEntry, TickerPriceTarget, TickerRecommendationEntry
from src.utils import get_yahoo_dataset_data

logger = logging.getLogger('apify')


@tool
async def tool_get_ticker_news(ticker: str) -> list[TickerNewsEntry]:
    """Tool to get recent news about a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        list[TickerNewsEntry]: Recent news about the ticker.

    Raises:
        RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_ticker_news')
    run_input = {
        'process': 'gn',
        'tickers': [f'{ticker}'],
    }
    if not (run := await Actor.apify_client.actor('canadesk/yahoo-finance').call(run_input=run_input)):
        msg = 'Failed to start the Actor canadesk/yahoo-finance!'
        raise RuntimeError(msg)

    dataset_id = run['defaultDatasetId']
    result = await get_yahoo_dataset_data(dataset_id)

    ticker_news = []
    for entry in result.get('data', []):
        content = entry.get('content', {})
        title = content.get('title')
        summary = content.get('summary')
        published_at = content.get('pubDate')
        provider = content.get('provider', {}).get('displayName')
        url = content.get('canonicalUrl', {}).get('url')

        if not all([title, summary, published_at, provider, url]):
            logger.warning('Skipping news entry with missing fields: %s', entry)
        ticker_news.append(
            TickerNewsEntry(
                ticker=ticker,
                title=title,
                summary=summary,
                published_at=published_at,
                provider=provider,
                url=url,
            )
        )
    return ticker_news


@tool
async def tool_get_ticker_price_targets(ticker: str) -> TickerPriceTarget | str:
    """Tool to get current price targets (analysis) for a ticker.

    Args:
        ticker (str): Ticker symbol.
        output (Literal['str', 'model']): Output format.
            'str' - return as string.
            'model' - return as Pydantic model.

    Returns:
        TickerPriceTarget: Current price targets.

    Raises:
            RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_ticker_price_targets')
    run_input = {
        'process': 'gp',
        'tickers': [f'{ticker}'],
    }
    if not (run := await Actor.apify_client.actor('canadesk/yahoo-finance').call(run_input=run_input)):
        msg = 'Failed to start the Actor canadesk/yahoo-finance!'
        raise RuntimeError(msg)

    dataset_id = run['defaultDatasetId']
    result = await get_yahoo_dataset_data(dataset_id)

    result.update(result.get('data', {}))
    del result['data']

    fields = ['ticker', 'current', 'low', 'high', 'mean', 'median']
    if not all(f in result for f in fields):
        msg = f'Dataset "{dataset_id}" does not contain required fields {fields}!'
        raise RuntimeError(msg)

    return TickerPriceTarget(
        ticker=result['ticker'],
        current_price=result['current'],
        analyst_price_target_low=result['low'],
        analyst_price_target_high=result['high'],
        analyst_price_target_mean=result['mean'],
        analyst_price_target_median=result['median'],
    )


@tool
async def tool_get_ticker_info(ticker: str) -> TickerInfo:
    """Tool to get information about a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        TickerInfo: Information about the ticker.

    Raises:
            RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_ticker_info')
    run_input = {
        'process': 'gi',
        'tickers': [f'{ticker}'],
    }
    if not (run := await Actor.apify_client.actor('canadesk/yahoo-finance').call(run_input=run_input)):
        msg = 'Failed to start the Actor canadesk/yahoo-finance!'
        raise RuntimeError(msg)

    dataset_id = run['defaultDatasetId']
    result = await get_yahoo_dataset_data(dataset_id)

    if not (data := result.get('data')):
        msg = f'Failed to get data from dataset "{dataset_id}"! Dataset does not contain "data" field.'
        raise RuntimeError(msg)
    # flatten dataset
    data['description'] = data.get('longBusinessSummary')
    result.update(data)
    del result['data']

    fields = ['ticker', 'sector', 'industry', 'description']
    if not all(f in result for f in fields):
        msg = f'Dataset "{dataset_id}" does not contain required fields {fields}!'
        raise RuntimeError(msg)

    return TickerInfo(**{f: result[f] for f in fields})


@tool
async def tool_get_ticker_recommendations(ticker: str) -> list[TickerRecommendationEntry]:
    """Tool to get recommendations for a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        list[TickerRecommendationEntry]: Recommendations for the ticker.

    Raises:
            RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_ticker_recommendations')
    run_input = {
        'process': 'gr',
        'tickers': [f'{ticker}'],
    }
    if not (run := await Actor.apify_client.actor('canadesk/yahoo-finance').call(run_input=run_input)):
        msg = 'Failed to start the Actor canadesk/yahoo-finance!'
        raise RuntimeError(msg)

    dataset_id = run['defaultDatasetId']
    result = await get_yahoo_dataset_data(dataset_id)

    ticker_recommendations = []
    for entry in result.get('data', []):
        period = entry.get('period')
        strongbuy = entry.get('strongbuy')
        buy = entry.get('buy')
        hold = entry.get('hold')
        sell = entry.get('sell')
        strongsell = entry.get('strongsell')

        if not all([period, strongbuy, buy, hold, sell, strongsell]):
            logger.warning('Skipping recommendation entry with missing fields: %s', entry)
        ticker_recommendations.append(
            TickerRecommendationEntry(
                ticker=ticker,
                period=period,
                recommendations_strong_buy=strongbuy,
                recommendations_buy=buy,
                recommendations_hold=hold,
                recommendations_sell=sell,
                recommendations_strong_sell=strongsell,
            )
        )

    return ticker_recommendations
