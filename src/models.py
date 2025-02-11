from pydantic import BaseModel, Field


class TickerPriceTarget(BaseModel):
    """Analyst price targets for a ticker."""

    ticker: str = Field(..., description='Ticker symbol')

    current_price: float = Field(..., description='Current price')
    analyst_price_target_low: float = Field(..., description='Analyst low price target')
    analyst_price_target_high: float = Field(..., description='Analyst high price target')
    analyst_price_target_mean: float = Field(..., description='Analyst mean price target')
    analyst_price_target_median: float = Field(..., description='Analyst median price target')


class TickerInfo(BaseModel):
    """Information about a ticker."""

    ticker: str = Field(..., description='Ticker symbol')

    sector: str = Field(..., description='Sector')
    industry: str = Field(..., description='Industry')
    description: str = Field(..., description='Description')


class TickerNewsEntry(BaseModel):
    """News entry about a ticker."""

    ticker: str = Field(..., description='Ticker symbol')

    title: str = Field(..., description='Title')
    url: str = Field(..., description='URL')
    provider: str = Field(..., description='Provider')
    published_at: str = Field(..., description='Published at')
    summary: str = Field(..., description='Summary')


class TickerRecommendationEntry(BaseModel):
    """Recommendation entry for a ticker."""

    ticker: str = Field(..., description='Ticker symbol')

    period: str = Field(..., description='Period')
    recommendations_strong_buy: int = Field(..., description='Number of strong buy recommendations')
    recommendations_buy: int = Field(..., description='Number of buy recommendations')
    recommendations_hold: int = Field(..., description='Number of hold recommendations')
    recommendations_sell: int = Field(..., description='Number of sell recommendations')
    recommendations_strong_sell: int = Field(..., description='Number of strong sell recommendations')


class SupervisorOutput(BaseModel):
    """Structured output from the supervisor agent."""

    next_agent: str = Field(..., description='Next agent to run')
    status: str = Field(
        ...,
        description=(
            'Current status of analysis, is one of the following:\n'
            'gathering and analyzing data...\n'
            'creating report...\n'
        ),
    )


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
    report: str = Field(..., description='Finance monitoring report')
