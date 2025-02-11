from pydantic import BaseModel, Field


class TickerPriceTarget(BaseModel):
    """Price target (analyst) for a ticker."""
    ticker: str = Field(..., description='Ticker symbol')

    current: float = Field(..., description='Current price')
    low: float = Field(..., description='Low price target')
    high: float = Field(..., description='High price target')
    mean: float = Field(..., description='Mean price target')
    median: float = Field(..., description='Median price target')

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
    strong_buy: int = Field(..., description='Number of strong buy recommendations')
    buy: int = Field(..., description='Number of buy recommendations')
    hold: int = Field(..., description='Number of hold recommendations')
    sell: int = Field(..., description='Number of sell recommendations')
    strong_sell: int = Field(..., description='Number of strong sell recommendations')


class OutputTickerReport(BaseModel):
    """Output report for a ticker from the AI agent."""
    ticker: str = Field(..., description='Ticker symbol')

    sentiment: str = Field(..., description='Ticker sentiment analysis (strong buy, buy, hold, sell, strong sell)')
    sentiment_reason: str = Field(
        ...,
        description=(
            'Reason for the sentiment analysis. '
            'Short reasoning about the sentiment (1-2 sentences at most).'
        )
    )
    report: str = Field(..., description='Finance monitoring report for the ticker')
