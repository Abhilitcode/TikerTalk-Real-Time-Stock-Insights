import streamlit as st
import openai
import requests
import plotly.graph_objects as go
import pandas as pd
import json
# from dotenv import load_dotenv
# import os
import requests

# Load .env file
# load_dotenv()

# Fetch the RapidAPI key
rapidapi_key = st.secrets["RAPIDAPI"]["KEY"]
newrapidapi_key = st.secrets["NEWRAPIDAPI"]["KEY"]
# Sidebar description
st.sidebar.title('Tiker Talk Application')
st.sidebar.write("""
    Welcome to the Tikker Talk Application! This app allows you to get information on:
    
    1. **Stock Data**: Get the latest stock price or data for any stock symbol (e.g., AAPL).
    2. **Stock News**: Stay updated with the latest news for any stock.
    3. **Profile**: Get detailed information about a stock's profile.
    4. **Stock Chart**: Visualize stock trends with charts.
    5. **Stock Analyst Recommendations**: See the latest analyst recommendations for a stock.
    
    ## How to Ask Questions:
    - **Stock Data**: 
        - "Give me latest stock price or data for AAPL?"
        - *Note: Using the stock symbol is compulsory for all queries.*
    
    - **Stock News**: 
        - "Give me latest news for AAPL?"
    
    - **Stock Profile**: 
        - "What is the profile for AAPL?"
    
    - **Stock Chart**: 
        - "Show me the chart for AAPL in US region for 1d with interval 5m?"
        - You can customize your chart with the following options:
            - **Region**: US, IN, JP, APAC, EU
            - **Range**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y
            - **Interval**: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
        - Example: "Show me the chart for AAPL in US region for 1d with interval 5m."
    
    - **Analyst Recommendations**: 
        - "Give me latest analyst recommendations for AAPL?"
    
    *Note: Always include the stock symbol (e.g., AAPL) when asking a question.*
""")

# Stock Symbol mapping (Company Name -> stock Symbol)
stock_mapping = {
'Microsoft': 'MSFT',
'Amazon': 'AMZN',
'Tesla': 'TSLA',
'Apple': 'AAPL',
'Johnson & Johnson': 'JNJ',
'Bank of America': 'BAC',
'Salesforce': 'CRM',
'AbbVie': 'ABBV',
'SAP SE': 'SAP',
'Sumitomo Mitsui Financial Group': 'SMFG',
'Chevron': 'CVX',
'ASML': 'ASML',
'Coca-Cola': 'KO',
'T-Mobile US': 'TMUS',
'Merck & Co.': 'MRK',
'Adobe': 'ADBE',
'Wells Fargo': 'WFC',
'Toyota Motor': 'TM',
'Cisco Systems': 'CSCO',
'Comcast': 'CCZ',
'ServiceNow': 'NOW',
'Accenture': 'ACN',
'PepsiCo': 'PEP',
'Alibaba': 'BABA',
'McDonald\'s': 'MCD',
'IBM': 'IBM',
'American Express': 'AXP',
'Linde': 'LIN',
'AstraZeneca': 'AZN',
'Berkshire Hathaway Inc.': 'BRK-B',
'JPMorgan Chase & Co.': 'JPM',
'Visa Inc.': 'V',
'Mastercard Incorporated': 'MA',
'Wells Fargo & Company': 'WFC',
'Blackstone Inc.': 'BX',
'The Goldman Sachs Group, Inc.': 'GS',
'Morgan Stanley': 'MS',
'Citigroup Inc.': 'C',
'Royal Bank of Canada': 'RY',
'BlackRock, Inc.': 'BLK',
'S&P Global Inc.': 'SPGI',
'The Charles Schwab Corporation': 'SCHW',
'KKR & Co. Inc.': 'KKR',
'The Progressive Corporation': 'PGR',
'Chubb Limited': 'CB',
'Marsh & McLennan Companies, Inc.': 'MMC',
'Apollo Global Management, Inc.': 'APO',
'The Toronto-Dominion Bank': 'TD',
'PayPal Holdings, Inc.': 'PYPL',
'Intercontinental Exchange, Inc.': 'ICE',
"Moody's Corporation": 'MCO',
'CME Group Inc.': 'CME'
}



# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI"]["KEY"]

# Fetch real-time stock data using Yahoo Finance API
def fetch_realtime_stock_data(ticker):
    #url stores the endpoint from where we get the data requested
    url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote"

    #these are params. The type parameter indicates that the request is for stock market data.
    querystring = {"ticker":ticker,"type":"STOCKS"}

    #headers r mainly used to authenticate api request.
    headers = {
    "x-rapidapi-key": rapidapi_key,
    "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    try:
      response = requests.get(url, headers=headers, params=querystring)
      response.raise_for_status()  # Raise an error for bad HTTP responses

      # Parse the response
      data = response.json()
      if 'body' in data:
          return data['body']  # Return the entire JSON data
      else:
          return {"error": "No data found for the provided ticker."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_analyst(symbol, region="US"):
    """
    Fetch analyst reports for a given stock ticker symbol.

    Parameters:
    symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT').
    region (str): The region for the stock (default is 'US').

    Returns:
    list: A list of dictionaries containing report details, excluding 'snapshot_url'.
    """
    url = "https://yahoo-finance166.p.rapidapi.com/api/stock/get-what-analysts-are-saying"
    querystring = {"region": region, "symbol": symbol}
    headers = {
        "x-rapidapi-key": newrapidapi_key,
        "x-rapidapi-host": "yahoo-finance166.p.rapidapi.com"
    }

    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        # Parse the response
        data = response.json()

        if data and "result" in data and isinstance(data["result"], list):
            analyst_reports = []
            for item in data["result"][0]["hits"]:
                # Extract only the necessary fields, excluding 'snapshot_url'
                report = {
                    "report_title": item.get("report_title", "No title available"),
                    # "investment_rating_status": item.get("investment_rating_status", "No status available"),
                    # "ticker": item.get("ticker", []),
                    "author": item.get("author", "Unknown author"),
                    "pdf_url": item.get("pdf_url", "No URL available"),
                    "report_type": item.get("report_type", "No type available"),
                    "abstract": item.get("abstract", "No abstract available"),
                    # "target_price_status": item.get("target_price_status", "No status available"),
                    # "investment_rating": item.get("investment_rating", "No rating available"),
                    # "target_price": item.get("target_price", "No target price available"),
                    "provider": item.get("provider", "Unknown provider"),
                    # "company_name": item.get("company_name", "No company name available"),
                    # "report_date": item.get("report_date", "No date available"),
                    
                }
                
                analyst_reports.append(report)
            return analyst_reports  # Return the list of analyst reports
        else:
            return {"error": "No analyst reports found for the provided symbol."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Example usage:
reports = get_analyst("AAPL")
if isinstance(reports, list):
    for report in reports:
        print(report)
else:
    print(reports)  # Print the error message


# Fetch real-time stock news
def fetch_realtime_news(ticker):
    """
    Fetch real-time stock data news for a given ticker symbol.

    Parameters:
    ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT').

    Returns:
    list: A list of dictionaries containing 'description', 'title', and 'pubDate'.
    """
    url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/news"
    querystring = {"ticker": ticker, "type": "ALL"}
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        # Parse the response
        data = response.json()

        if data and 'body' in data:  # Check if 'body' exists in the response
            news_items = []
            for item in data['body']:
                # Extract only the necessary fields: description, title, and pubDate
                news_item = {
                    'description': item.get('description', 'No description available'),
                    'title': item.get('title', 'No title available'),
                    'pubDate': item.get('pubDate', 'No publication date available')
                }
                news_items.append(news_item)
            return news_items  # Return the list of news items with required fields
        else:
            return {"error": "No news data found for the provided ticker."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

#3rd api fetch the profile
def fetch_stock_profile(ticker, module):
    """
    Fetches stock data from the Yahoo Finance API for the given ticker and module.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL" for Apple).
        module (str): The financial data module to retrieve (e.g., "asset-profile").
        api_key (str): Your RapidAPI key for authentication.

    Returns:
        dict: The JSON response from the API.
    """
    url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/modules"
    
    querystring = {"ticker": ticker, "module": module}
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        if 'body' in data:
            return data['body']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to fetch stock chart data using Yahoo Finance API
def fetch_stock_chart(stock_name, region, range, interval):
    """
    Fetches and plots the stock chart for a given symbol.

    Parameters:
        symbol (str): Stock symbol (e.g., "AAPL").
        region (str): Region code (default is "US").
        range (str): Range of data (e.g., "1d" for one day).
        interval (str): Interval between data points (e.g., "5m" for 5 minutes).

    Returns:
        None
    """
    url = "https://yahoo-finance166.p.rapidapi.com/api/stock/get-chart"
    querystring = {"region": region, "range": range, "symbol": stock_name, "interval": interval}
    headers = {
        "x-rapidapi-key": newrapidapi_key,
        "x-rapidapi-host": "yahoo-finance166.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        # Extract timestamps and closing prices
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            timestamps = data['chart']['result'][0]['timestamp']
            close_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
            
            # Convert timestamps to readable dates
            readable_timestamps = [pd.to_datetime(ts, unit='s') for ts in timestamps]

            # Plot using plotly for interactive chart
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=readable_timestamps,
                y=close_prices,
                mode='lines+markers',
                name=f"Stock Price: {stock_name}",
                line=dict(color='blue'),
                marker=dict(symbol='circle', size=6)
            ))

            fig.update_layout(
                title=f"Stock Chart for {stock_name}",
                xaxis_title="Time",
                yaxis_title="Close Price",
                template="plotly_dark",
                xaxis_rangeslider_visible=True
            )

            # Display interactive chart in Streamlit
            st.plotly_chart(fig)
        else:
            st.error("Chart data is not available.")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

#Function to get stock chart
def get_stock_chart(stock_name, region, range, interval):
    data = fetch_stock_chart(stock_name, region, range, interval)
    return data


# Functions for interacting with OpenAI's GPT model
def get_stock_data(stock_name):
    data = fetch_realtime_stock_data(stock_name)
    return data

def get_stock_news(stock_name):
    news = fetch_realtime_news(stock_name)
    return news

def get_stock_profile(stock_name, module):
    profile = fetch_stock_profile(stock_name, module)
    return profile

def get_analyst_data(symbol, region):
    analyst_data = get_analyst(symbol)
    return analyst_data

# Streamlit app UI
st.title("TikerTalk: Real-Time Stock Insights")

# Dropdown for stock selection
stock_name = st.selectbox("Select Stock Ticker", list(stock_mapping.keys()))

# Display the symbol for the selected company
if stock_name:
    stock_symbol = stock_mapping[stock_name]
    st.write(f"The selected stock symbol for {stock_name} is **{stock_symbol}**")

# Textbox for user to ask questions
question = st.text_input(
    "Ask a question about the stock (e.g., 'What is the latest price/ profile/ news for BABA?' or show me the chart for AAPL in US region for 1d with interval 5m?)"
)

# Note to remind users to include a stock symbol
st.warning("**Note: Do not forget to include a stock symbol (e.g., AAPL) in your question.**")

# # Dropdown for region selection
# region = st.selectbox("Select Region", ["US", "EU", "JP","IN","APAC"])

# # Dropdown for range selection
# range_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"]
# range = st.selectbox("Select Range", range_options)

# # Dropdown for interval selection
# interval_options = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
# interval = st.selectbox("Select Interval", interval_options)


# Button to submit the question
if st.button("Submit"):
    if question:
        # Use OpenAI to determine whether to fetch stock data or news
        messages = [{"role": "user", "content": question}]
        functions = [
            {
                "name": "get_stock_news",
                "description": "Fetch the latest news for a stock.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stock_name": {
                            "type": "string",
                            "description": "Name of the stock",
                        }
                    },
                    "required": ["stock_name"],
                },
            },
            {
                "name": "get_stock_data",
                "description": "Fetch key data about a stock, or stock data such as price and P/E ratio.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stock_name": {
                            "type": "string",
                            "description": "Name of the stock",
                        }
                    },
                    "required": ["stock_name"],
                },
            },
            {
                    "name": "get_stock_profile",
                    "description": "Fetch the company profile of a stock.",
                    "parameters": {
                        "type": "object",
                        "properties": {"stock_name": {"type": "string"}},
                        "required": ["stock_name"],
                    },
            },
            {
                    "name": "get_stock_chart",
                    "description": "Fetch the company chart or dashboard or analytics of a stock.",
                    "parameters": {
                        "type": "object",
                        "properties": {"stock_name": {"type": "string"},
                                       "region": {"type": "string", "enum": ["US", "IN", "JP", "APAC","EU"]},
                                        "range": {"type": "string", "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"]},
                                        "interval": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]}},
                        "required": ["stock_name", "region", "range", "interval"],
                    },
            },
            {
                    "name": "get_analyst_data",
                    "description": "Fetch the analyst recommendations or what analyst has to say about stock?",
                    "parameters": {
                        "type": "object",
                        "properties": {"symbol": {"type": "string"}},
                                    #    "region": {"type": "string", "enum": ["US", "IN", "JP", "APAC","EU"]},
                                    #     "range": {"type": "string", "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"]},
                                    #     "interval": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]}},
                        "required": ["symbol"],
                    },
            }
        ]

        # Call OpenAI API to decide which function to run
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        function_name = response["choices"][0]["message"]["function_call"]["name"]
        args = eval(response["choices"][0]["message"]["function_call"]["arguments"])

        # Based on the response, either fetch stock data or news
        if function_name == "get_stock_news":
            stock_name = args["stock_name"]
            news = get_stock_news(stock_name)
            st.subheader("Latest News")
            # Convert the JSON response into string
            # news_string = json.dumps(news, indent=4)
            # st.write(news_string)  # Display the JSON as string
            st.write(news)
        elif function_name == "get_stock_data":
            stock_name = args["stock_name"]
            data = get_stock_data(stock_name)
            st.subheader("Stock Data")
            st.write(data)
        elif function_name == "get_stock_profile":
            stock_name = args['stock_name']
            data = get_stock_profile(stock_name,"asset-profile")
            st.subheader("Stock Profile")
            if data:
                st.write(data)
            else:
                print("Could not fetch the stock data.")
        elif function_name == "get_stock_chart":
            stock_name = args['stock_name']
            region = args["region"]
            range = args["range"]
            interval = args["interval"]
            st.subheader(f"Stock chart for {stock_name} in the {region} region with a range of {range} and an interval of {interval}")
            data = get_stock_chart(stock_name, region, range, interval)
            if data:
                st.write(data)
            else:
                st.write("Could not fetch the stock chart data.")

        elif function_name == "get_analyst_data":
            symbol = args['symbol']
            st.subheader(f"Analyst Recommendations for {stock_name}")
            data = get_analyst_data(symbol, region='US')
            if data:
                st.write(data)
            else:
                st.write("Could not fetch analyst recommendations.")

        
        else:
            st.write("Please ask a question to proceed.")

# # Display a warning message
# st.warning("Select the appropriate options below only when you want to extract a stock chart.")

# # Dropdown for region selection
# region = st.selectbox("Select Region", ["US", "EU", "JP","IN","APAC"])

# # Dropdown for range selection
# range_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"]
# range = st.selectbox("Select Range", range_options)

# # Dropdown for interval selection
# interval_options = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
# interval = st.selectbox("Select Interval", interval_options)

# if st.button("Fetch Stock Chart"):
#     if stock_symbol:
#         fetch_stock_chart(stock_symbol, region, range, interval)
