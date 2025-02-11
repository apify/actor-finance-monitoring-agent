import logging
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from src.models import TickerInfo, TickerNewsEntry, TickerPriceTarget, TickerRecommendationEntry
from src.utils import get_yahoo_dataset_data, run_async

logger = logging.getLogger('apify')

@tool
def tool_get_ticker_news(ticker: str) -> list[TickerNewsEntry]:
    """Tool to get recent news about a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        list[TickerNewsEntry]: Recent news about the ticker.
    """
    print('tool_get_ticker_news')
    assert ticker
    dataset_id = '4NG1scPdVBRIhYGFe'
    result = run_async(get_yahoo_dataset_data(dataset_id))

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
        ticker_news.append(TickerNewsEntry(
            ticker=ticker,
            title=title,
            summary=summary,
            published_at=published_at,
            provider=provider,
            url=url,
        ))
    return ticker_news


@tool
def tool_get_ticket_price_targets(ticker: str) -> TickerPriceTarget:
    """Tool to get current price targets (analysis) for a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        TickerPriceTarget: Current price targets.
    """
    print('tool_get_ticket_price_targets')
    assert ticker
    dataset_id = '18rhSER1HTaKcq5lc'
    result = run_async(get_yahoo_dataset_data(dataset_id))

    result.update(result.get('data', {}))
    del result['data']

    fields = ['ticker', 'current', 'low', 'high', 'mean', 'median']
    if not all(f in result for f in fields):
        msg = f'Dataset "{dataset_id}" does not contain required fields {fields}!'
        raise RuntimeError(msg)

    return TickerPriceTarget(**{f: result[f] for f in fields})

@tool
def tool_get_ticker_info(ticker: str) -> TickerInfo:
    """Tool to get information about a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        TickerInfo: Information about the ticker.
    """
    print('tool_get_ticker_info')
    assert ticker
    dataset_id = '7EENr5QdvxCTQOdmp'
    result = run_async(get_yahoo_dataset_data(dataset_id))

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
def tool_get_ticker_recommendations(ticker: str) -> list[TickerRecommendationEntry]:
    """Tool to get recommendations for a ticker.

    Args:
        ticker (str): Ticker symbol.

    Returns:
        list[TickerRecommendationEntry]: Recommendations for the ticker.
    """
    print('tool_get_ticker_recommendations')
    assert ticker
    dataset_id = 'vt4ZjUpiTkA53gsnu'
    result = run_async(get_yahoo_dataset_data(dataset_id))

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
        ticker_recommendations.append(TickerRecommendationEntry(
            ticker=ticker,
            period=period,
            strong_buy=strongbuy,
            buy=buy,
            hold=hold,
            sell=sell,
            strong_sell=strongsell,
        ))

    return ticker_recommendations

TOOLS = [tool_get_ticker_news, tool_get_ticket_price_targets, tool_get_ticker_info,
    tool_get_ticker_recommendations]
