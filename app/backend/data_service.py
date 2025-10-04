import yfinance as yf
import pandas as pd
import numpy as np
import feedparser
from textblob import TextBlob
from db_config import db

# -------- Market Data --------
def fetch_market_data(symbol: str):
    df = yf.download(symbol, period="2y", interval="1d").dropna()
    if df.empty:
        return None

    # Moving Averages: 7-day, 14-day, 30-day
    df["SMA_7"] = df["Close"].rolling(window=7).mean()
    df["SMA_14"] = df["Close"].rolling(window=14).mean()
    df["SMA_30"] = df["Close"].rolling(window=30).mean()
    
    # Exponential Moving Averages
    df["EMA_7"] = df["Close"].ewm(span=7, adjust=False).mean()
    df["EMA_14"] = df["Close"].ewm(span=14, adjust=False).mean()
    df["EMA_30"] = df["Close"].ewm(span=30, adjust=False).mean()

    # Daily Return: (Close_t - Close_(t-1)) / Close_(t-1)
    df["Daily_Return"] = df["Close"].pct_change()
    
    # Volatility: 14-day rolling standard deviation
    df["Volatility"] = df["Daily_Return"].rolling(window=14).std()

    df.reset_index(inplace=True)
    df["Symbol"] = symbol
    
    # Flatten multi-level columns if they exist
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    return df

# -------- Sentiment Analysis --------
def fetch_sentiment(symbol: str, limit=20):
    import urllib.parse
    query = f"{symbol} stock" if "-" not in symbol else symbol.replace("-", " ")
    encoded_query = urllib.parse.quote(query)
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded_query}+finance&hl=en")
    sentiments = []
    for entry in feed.entries[:limit]:
        # Use only title for sentiment analysis to avoid HTML noise in summary
        text = entry.title
        polarity = TextBlob(text).sentiment.polarity
        
        # Enhanced sentiment analysis for financial news
        positive_keywords = ['surge', 'surges', 'surged', 'rally', 'rallies', 'rise', 'rises', 'rose', 'high', 'higher', 'highest', 'gain', 'gains', 'gained', 'boost', 'boosted', 'profit', 'profits', 'beat', 'beats', 'beat', 'exceed', 'exceeds', 'exceeded', 'strong', 'stronger', 'bullish', 'optimistic', 'breakthrough', 'milestone', 'record', 'best', 'outperform', 'outperforming']
        negative_keywords = ['fall', 'falls', 'fell', 'drop', 'drops', 'dropped', 'decline', 'declines', 'declined', 'crash', 'crashes', 'crashed', 'loss', 'losses', 'lost', 'miss', 'misses', 'missed', 'weak', 'weaker', 'weakest', 'bearish', 'pessimistic', 'concern', 'concerns', 'risk', 'risks', 'plunge', 'plunges', 'plunged', 'tumble', 'tumbles', 'tumbled', 'slump', 'slumps', 'slumped']
        
        text_lower = text.lower()
        
        # More precise keyword matching - avoid false positives
        positive_count = 0
        negative_count = 0
        
        # Check for positive keywords
        for word in positive_keywords:
            if word in text_lower:
                positive_count += 1
                
        # Check for negative keywords (avoid words that appear in positive contexts)
        for word in negative_keywords:
            if word in text_lower:
                # Avoid false positives like "down" in "shutdown"
                if word == 'down' and 'shut' in text_lower:
                    continue
                negative_count += 1
        
        # Sentiment analysis complete
        
        # Enhanced classification logic
        if negative_count > positive_count:
            sentiment_class = "negative"
        elif positive_count > negative_count or polarity > 0.05:
            sentiment_class = "positive"
        elif polarity < -0.05:
            sentiment_class = "negative"
        else:
            sentiment_class = "neutral"
            
        # Convert published date to datetime for time-series collection
        from datetime import datetime
        published_date = None
        if hasattr(entry, 'published'):
            try:
                published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
            except:
                published_date = datetime.now()
        
        sentiments.append({
            "symbol": symbol,
            "title": entry.title,
            "summary": entry.summary,
            "link": entry.link,
            "polarity": round(polarity, 4),
            "sentiment": sentiment_class,
            "published": published_date
        })
    return sentiments

# -------- Store in MongoDB --------
def store_data(symbol: str, market_df: pd.DataFrame, sentiments: list):
    # Skip delete operations for time-series collections and just insert
    # db.historical_data.delete_many({"Symbol": symbol})  # Not allowed in time-series
    # db.sentiments.delete_many({"symbol": symbol})       # Not allowed in time-series
    db.historical_data.insert_many(market_df.to_dict("records"))
    if sentiments:
        db.sentiments.insert_many(sentiments)

# -------- Main Orchestrator --------
def fetch_and_store(symbol: str):
    market_df = fetch_market_data(symbol)
    if market_df is None:
        return {"error": "No market data found"}

    sentiments = fetch_sentiment(symbol)
    store_data(symbol, market_df, sentiments)

    return {
        "message": f"{symbol} data (market + sentiment) stored successfully",
        "records": len(market_df),
        "sentiment_count": len(sentiments)
    }

# -------- Retrieve Sample --------
def get_data(symbol: str):
    prices = list(db.historical_data.find({"Symbol": symbol}, {"_id": 0}).limit(10))
    news = list(db.sentiments.find({"symbol": symbol}, {"_id": 0}).limit(5))
    return {"symbol": symbol, "sample_prices": prices, "sample_news": news}
