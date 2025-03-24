# Finance Monitoring Agent 📊💹


[![Agent Actor Inspector](https://apify.com/actor-badge?actor=jakub.kopecky/finance-monitoring-agent)](https://apify.com/jakub.kopecky/finance-monitoring-agent)
[![GitHub Repo stars](https://img.shields.io/github/stars/apify/actor-finance-monitoring-agent)](https://github.com/apify/actor-finance-monitoring-agent/stargazers)

The **Finance Monitoring Agent** is an Apify AI Actor tailored for investors and analysts, providing comprehensive analysis of specific stock tickers. It gathers, processes, and produces insightful reports to help understand market trends, performance metrics, and sentiment analysis.

## 🌟 What is Finance Monitoring Agent?

This agent is designed to:

- **Analyze stock tickers**: Focuses on specific stocks to deliver detailed performance insights.
- **Generate reports**: Creates structured reports in markdown format, summarizing key financial data, trends, and sentiment analysis.
- **Leverage AI**: Utilizes OpenAI's capabilities, allowing customization between more advanced (GPT-4o) or faster, cheaper (GPT-4o Mini) models for analysis.
- **Provide downloadable output**: The **report.md** file can be downloaded from the **key-value store** in the storage section of the Actor run details.


---

## 🎯 Features of Finance Monitoring AI Agent

- **Detailed Stock Analysis**: Provides in-depth analysis including sentiment, performance, and market trends.
- **Customizable AI Models**: Choose between gpt-4o, gpt-4o-mini and the reasoning models o1 and o3-mini.

---

## 📈 Data Providers

The **Finance Monitoring Agent** leverages multiple data sources to ensure comprehensive and accurate analysis:

- **Google Finance**: Provides essential ticker information and financial data for the ticker analysis. Using [Google Finance](https://apify.com/scraped_org/google-finance-scraper) Apify Actor.
- **Google News**: Searches for relevant news articles to include in the sentiment analysis and overall report. Using [Google News Scraper](https://apify.com/lhotanova/google-news-scraper) Apify Actor.

---

## 🚀 How it works

1. **Input**: Specify the stock ticker, choose your AI model, and provide your OpenAI API key.
2. **Processing**: The agent fetches real-time data, processes it using the selected AI model, and compiles a report.
3. **Output**: Generates a markdown report with analysis, which is pushed to Apify's dataset for review.

### 💰 Pricing

This Actor uses the [Pay Per Event](https://docs.apify.com/sdk/js/docs/next/guides/pay-per-event) (PPE) monetization model, which provides flexible pricing based on defined events. Currently the Actor charges for Actor startup and for total token usage (based on OpenAI API output token price).

The Actor's pricing is based on the following events:

| Event | Price (USD) |
|-------|-------------|
| Actor startup (each 1 GB of memory) | $0.005 |
| gpt-4o (100 tokens) | $0.001 |
| gpt-4o-mini (100 tokens) | $0.00006 |
| o1 (100 tokens) | $0.006 |
| o3-mini (100 tokens) | $0.00044 |

### Input Example

```json
{
  "ticker": "TSLA",
  "model": "gpt-4o",
}
```

### Output Example

Sample report from the **Finance Monitoring Agent** for the `TSLA` ticker is available [here](docs/report.md).

Actor dataset output with structured sentiment analysis looks like this:
```json
{
  "ticker": "TSLA",
  "sentiment": "hold",
  "sentiment_reason": "Despite strong market position, the recall and negative outlook...",
  "report": "..."
}
```

---

## ✨ Why use Finance Monitoring AI Agent?

- **Time Efficiency**: Automates the analysis process, providing quick insights without manual data crunching.
- **Enhanced Decision Making**: Offers sentiment analysis alongside performance metrics, aiding in investment decisions.
- **Scalability**: Can analyze multiple tickers by running multiple instances of the Actor in parallel.
- **AI-Driven Insights**: Leverages the latest in AI technology for nuanced market analysis.

---

## 🔧 Technical Highlights

- **Built with Apify SDK**: Ensures robust, scalable web scraping and data processing.
- **AI Integration**: Seamless interaction with OpenAI models for dynamic content generation.

---

## 📖 Learn more

- [Apify platform](https://apify.com)
- [Apify SDK documentation](https://docs.apify.com/sdk/python)
- [What are AI Agents?](https://blog.apify.com/what-are-ai-agents/)
- [AI agent architecture](https://blog.apify.com/ai-agent-architecture)
- [How to build an AI agent on Apify](https://blog.apify.com/how-to-build-an-ai-agent/)

---

Start leveraging AI for your financial analysis today and make informed investment decisions with ease! 📈🤖

---

🌐 Open source

This Actor is open source, hosted on [GitHub](https://github.com/apify/actor-finance-monitoring-agent).

---

## Development

Clone the repository and install the dependencies:

```bash
git clone https://github.com/apify/finance-monitoring-agent
cd finance-monitoring-agent

uv sync
# or make install-dev
```

To run the Actor locally, use the following command:

```bash
apify run -p -i '{"ticker": "TSLA", "model": "gpt-4o"}'
# in debug mode
#apify run -p -i '{"debug": true, "ticker": "TSLA", "model": "gpt-4o"}'
```

The output report will be saved in the **storage/key_value_stores/default/** directory.
