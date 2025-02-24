"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://python.langchain.com/docs/concepts/tools/
- https://python.langchain.com/docs/how_to/#tools
"""

import datetime
import logging

from apify import Actor
from langchain_core.tools import tool

from src.models import (
    GoogleTickerInfo,
    GoogleTickerInfoYearlyFinancials,
    TickerInfo,
    TickerNewsEntry,
    TickerPriceTarget,
    TickerRecommendationEntry,
)
from src.utils import get_yahoo_dataset_data, run_actor_get_default_dataset

logger = logging.getLogger('apify')


@tool
async def tool_get_google_news(query: str, date_from: str, max_items: int = 25) -> list[TickerNewsEntry]:
    """Tool to get recent news from Google News (can be used to get news about a ticker).

    Args:
        query (str): Query string.
        date_from (str): Date from which to get news in format 'YYYY-MM-DD'.
        max_items (int): Maximum number of news items to return.

    Returns:
        list[TickerNewsEntry]: Recent news.
    """
    logger.debug('Running tool: tool_get_google_news')

    # check date, raises ValueError if invalid
    datetime.datetime.strptime(date_from, '%Y-%m-%d')  # noqa: DTZ007

    run_input = {
        'query': query,
        'dateFrom': date_from,
        'maxItems': max_items,
        'extractImages': False,
        'language': 'US:en',
    }
    actor_id = 'lhotanova/google-news-scraper'
    _, dataset_items = await run_actor_get_default_dataset(actor_id, run_input)

    google_news = []
    for entry in dataset_items:
        title = entry.get('title')
        published_at = entry.get('publishedAt')
        provider = entry.get('source')
        url = entry.get('link')

        if not all([title, published_at, provider, url]):
            logger.warning('Skipping news entry with missing fields: %s', entry)
            continue
        google_news.append(
            TickerNewsEntry(
                title=str(title),
                published_at=str(published_at),
                provider=str(provider),
                url=str(url),
            )
        )
    return google_news


@tool
async def tool_get_google_ticker_info(ticker: str) -> GoogleTickerInfo:
    """Tool to get information about a ticker from Google Finance.

    Information includes ticker description, CEO and key stocks financials data.

    Args:
        ticker (str): Ticker symbol, for example 'TSLA'.

    Returns:
        GoogleTickerInfo: Ticker information.

    Raises:
        RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_google_ticker_info')

    # First search for the eschange the ticker uses
    actor_id = 'scraped_org/google-finance-scraper'
    run_input = {
      "action": "search_stocks",
      "proxy": {
        "useApifyProxy": True
      },
      "search_stocks": ticker,
    }
    dataset_id, dataset_items = await run_actor_get_default_dataset(actor_id, run_input)
    if not dataset_items:
        msg = f'Could not find ticker {ticker} in Google Finance'
        raise RuntimeError(msg)

    # Get the stock id
    stock_id = None
    for item in dataset_items:
        if (_ticker := item.get('ticker')) == ticker and (_stock_id := item.get('stock_id')):
            stock_id = _stock_id
            break
    if not stock_id:
        msg = f'Could not find ticker {ticker} in Google Finance'
        raise RuntimeError(msg)

    run_input = {
        'action': 'stocks_details',
        'extract_quarterly_financial': True,
        'extract_stock_news': True,
        'extract_stock_prices_in_day': True,
        'extract_stock_prices_last_30_days': True,
        'extract_yearly_financial': True,
        'proxy': {'useApifyProxy': True},
        'stocks': [stock_id],
        'country': 'us',
        'language': 'en',
        'market_trends_types': ['most-active'],
    }
    actor_id = 'scraped_org/google-finance-scraper'
    dataset_id, dataset_items = await run_actor_get_default_dataset(actor_id, run_input)

    if not dataset_items:
        msg = f'Failed to get data from dataset "{dataset_id}"! Dataset is empty.'
        raise RuntimeError(msg)

    data = dataset_items[0]

    return GoogleTickerInfo(
        current_price=data.get('stock_details', {}).get('current_price'),
        about=data.get('stock_about', {}).get('about'),
        ceo=data.get('stock_about', {}).get('CEO'),
        founded=data.get('stock_about', {}).get('founded'),
        pe_ratio=data.get('stock_details', {}).get('pe_ratio'),
        price_year_range=(
            data.get('stock_details', {}).get('year_range', {}).get('min'),
            data.get('stock_details', {}).get('year_range', {}).get('max'),
        ),
        yerly_financials=[
            GoogleTickerInfoYearlyFinancials(
                year=financial.get('year'),
                earning_per_share=financial.get('earning_per_share'),
                net_profit_margin=financial.get('net_profit_margin'),
                return_on_capital=financial.get('return_on_capital'),
                effective_tax_rate=financial.get('effective_tax_rate'),
                return_on_assets=financial.get('return_on_assets'),
                price_to_book=financial.get('price_to_book'),
            )
            for financial in data.get('financials', {}).get('yearly_financial', [])
        ],
    )


# Yahoo tools are currently broken - scraper is not working #
@tool
async def tool_get_yahoo_ticker_news(ticker: str) -> list[TickerNewsEntry]:
    """Tool to get recent news from Yahoo Finance about a ticker.

    Args:
        ticker (str): Ticker symbol, for example 'TSLA'.

    Returns:
        list[TickerNewsEntry]: Recent news about the ticker.

    Raises:
        RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_yahoo_ticker_news')
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
            continue
        ticker_news.append(
            TickerNewsEntry(
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
        ticker (str): Ticker symbol, for example 'TSLA'.
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
        msg = (
            f'Dataset "{dataset_id}" does not contain required fields {fields}! '
            f'It is possible that the ticker "{ticker}" is incorrect.'
        )
        raise RuntimeError(msg)

    return TickerPriceTarget(
        current_price=result['current'],
        analyst_price_target_low=result['low'],
        analyst_price_target_high=result['high'],
        analyst_price_target_mean=result['mean'],
        analyst_price_target_median=result['median'],
    )


@tool
async def tool_get_ticker_basic_info(ticker: str) -> TickerInfo:
    """Tool to get basic information about a ticker.

    Args:
        ticker (str): Ticker symbol, for example 'TSLA'.

    Returns:
        TickerInfo: Basic information about the ticker.

    Raises:
        RuntimeError: If dataset does not contain required fields.
    """
    logger.debug('Running tool: tool_get_ticker_basic_info')
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
        msg = (
            f'Dataset "{dataset_id}" does not contain required fields {fields}! '
            f'It is possible that the ticker "{ticker}" is incorrect.'
        )
        raise RuntimeError(msg)

    return TickerInfo(**{f: result[f] for f in fields})


@tool
async def tool_get_ticker_recommendations(ticker: str) -> list[TickerRecommendationEntry]:
    """Tool to get recommendations for a ticker.

    Args:
        ticker (str): Ticker symbol, for example 'TSLA'.

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
                period=period,
                recommendations_strong_buy=strongbuy,
                recommendations_buy=buy,
                recommendations_hold=hold,
                recommendations_sell=sell,
                recommendations_strong_sell=strongsell,
            )
        )

    return ticker_recommendations
