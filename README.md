# Finance Monitoring Agent 📊💹

The **Finance Monitoring Agent** is an Apify AI Actor tailored for investors and analysts, providing comprehensive analysis of specific stock tickers. It gathers, processes, and produces insightful reports to help understand market trends, performance metrics, and sentiment analysis.

## 🌟 What is Finance Monitoring Agent?

This agent is designed to:

- **Analyze stock tickers**: Focuses on specific stocks to deliver detailed performance insights.
- **Generate reports**: Creates structured reports in markdown format, summarizing key financial data, trends, and sentiment analysis.
- **Leverage AI**: Utilizes OpenAI's capabilities, allowing customization between more advanced (GPT-4o) or faster, cheaper (GPT-4o Mini) models for analysis.
- **Provide downloadable output**: The **report.md** file can be downloaded from the **key-value store** in the storage section of the Actor run details.

### Sample Output

Sample report from the **Finance Monitoring Agent** for the `TSLA` ticker is available [here](docs/report.md).

---

## 🎯 Features of Finance Monitoring AI Agent

- **Detailed Stock Analysis**: Provides in-depth analysis including sentiment, performance, and market trends.
- **Customizable AI Models**: Choose between GPT-4o for detailed analysis or GPT-4o Mini for quicker results.

---

## 🚀 How it works

1. **Input**: Specify the stock ticker, choose your AI model, and provide your OpenAI API key.
2. **Processing**: The agent fetches real-time data, processes it using the selected AI model, and compiles a report.
3. **Output**: Generates a markdown report with analysis, which is pushed to Apify's dataset for review.

### Input Example

```json
{
  "ticker": "TSLA",
  "model": "gpt-4o",
  "openai_api_key": "your_openai_api_key_here",
}
```


### Output Example
```json
{
  "ticker": "TSLA",
  "sentiment": "hold",
  "sentiment_reason": "The sentiment is derived from a mixed outlook among analysts...",
  "report": "# Tesla, Inc. Financial Report - February 11, 2025 ## Executive Summary Tesla, Inc., under the leadership of Elon Musk, continues to be a significant player in the electric vehicle and clean energy sectors..."
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
- **Security**: Uses environment variables for API keys, enhancing security.
- **Extensibility**: Can be modified to include additional financial metrics or data sources.

---

## 📖 Learn more

- [Apify platform](https://apify.com)
- [Apify SDK documentation](https://docs.apify.com/sdk/python)

---

Start leveraging AI for your financial analysis today and make informed investment decisions with ease! 📈🤖
