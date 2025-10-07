import axios from "axios";
const BASE_URL = "http://127.0.0.1:8001";

// Legacy endpoints (from Part 1)
export const fetchData = async (symbol) => {
  try {
    const res = await axios.get(`${BASE_URL}/fetch-data/${symbol}`);
    return res.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export const getData = async (symbol) => {
  try {
    const res = await axios.get(`${BASE_URL}/get-data/${symbol}`);
    return res.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

// New endpoints for Part 3
export const fetchInstruments = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/get_instruments`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch instruments: ${error.message}`);
  }
};

export const fetchHistoricalData = async (symbol, limit = 100) => {
  try {
    const response = await axios.get(`${BASE_URL}/get_historical/${symbol}?limit=${limit}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch historical data for ${symbol}: ${error.message}`);
  }
};

export const fetchForecast = async (symbol, horizon = 24, model = 'ensemble') => {
  try {
    const response = await axios.get(`${BASE_URL}/forecast/${symbol}?horizon=${horizon}&model=${model}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch forecast for ${symbol}: ${error.message}`);
  }
};

export const fetchSentiment = async (symbol) => {
  try {
    const response = await axios.get(`${BASE_URL}/get-data/${symbol}`);
    const news = response.data.sample_news || [];
    
    if (news.length === 0) {
      return { sentiment: 'neutral', polarity: 0, title: null };
    }
    
    // Calculate average sentiment from recent news
    const sentiments = news.map(item => ({
      sentiment: item.sentiment,
      polarity: item.polarity || 0,
      title: item.title
    }));
    
    const avgPolarity = sentiments.reduce((sum, s) => sum + s.polarity, 0) / sentiments.length;
    
    let overallSentiment = 'neutral';
    if (avgPolarity > 0.1) overallSentiment = 'positive';
    else if (avgPolarity < -0.1) overallSentiment = 'negative';
    
    return {
      sentiment: overallSentiment,
      polarity: avgPolarity,
      title: sentiments[0]?.title || null
    };
  } catch (error) {
    throw new Error(`Failed to fetch sentiment for ${symbol}: ${error.message}`);
  }
};

export const healthCheck = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    return response.data;
  } catch (error) {
    throw new Error(`Health check failed: ${error.message}`);
  }
};
