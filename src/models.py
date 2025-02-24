"""This module defines Pydantic models for this project.

These models are used mainly for the structured tool and LLM outputs.
"""

from pydantic import BaseModel, Field


class GoogleTickerInfoYearlyFinancials(BaseModel):
    """Yearly financials for a ticker from Google Finance."""

    year: int = Field(..., description='Year')
    earning_per_share: float | None = Field(None, description='Earnings per share')
    net_profit_margin: float | None = Field(None, description='Net profit margin percentage')
    return_on_capital: float | None = Field(None, description='Return on capital percentage')
    effective_tax_rate: float | None = Field(None, description='Effective tax rate percentage')
    return_on_assets: float | None = Field(None, description='Return on assets percentage')
    price_to_book: float | None = Field(None, description='Price to book ratio')


class GoogleTickerInfo(BaseModel):
    """Information about a ticker from Google Finance."""

    current_price: float = Field(..., description='Current price')
    about: str = Field(..., description='Ticker description')
    ceo: str = Field(..., description='Ticker CEO')
    founded: str = Field(..., description='Ticker founding date')
    price_year_range: tuple[float, float] | None = Field(None, description='52-week price range')
    pe_ratio: float | None = Field(None, description='PE ratio')
    yerly_financials: list[GoogleTickerInfoYearlyFinancials] = Field(..., description='Yearly financials')


class TickerPriceTarget(BaseModel):
    """Analyst price targets for a ticker."""

    current_price: float
    analyst_price_target_low: float
    analyst_price_target_high: float
    analyst_price_target_mean: float
    analyst_price_target_median: float


class TickerInfo(BaseModel):
    """Information about a ticker."""

    sector: str
    industry: str
    description: str


class TickerNewsEntry(BaseModel):
    """News entry about a ticker."""

    title: str
    provider: str = Field(..., description='Provider of the news')
    published_at: str
    summary: str | None = None
    url: str


class TickerRecommendationEntry(BaseModel):
    """Recommendation entry for a ticker."""

    period: str = Field(..., description='Period')
    recommendations_strong_buy: int = Field(..., description='Number of strong buy recommendations')
    recommendations_buy: int = Field(..., description='Number of buy recommendations')
    recommendations_hold: int = Field(..., description='Number of hold recommendations')
    recommendations_sell: int = Field(..., description='Number of sell recommendations')
    recommendations_strong_sell: int = Field(..., description='Number of strong sell recommendations')


class OutputTickerReport(BaseModel):
    """Structured output report for a ticker from the report agent."""

    ticker: str = Field(..., description='Ticker symbol')

    sentiment: str = Field(
        ..., description='Ticker sentiment analysis one of strong buy, buy, hold, sell or strong sell (case-sensitive)'
    )
    sentiment_reason: str = Field(
        ...,
        description=('Reason for the sentiment analysis. Short reasoning about the sentiment (1-2 sentences at most).'),
    )
    report: str = Field(..., description='Financial monitoring report')
