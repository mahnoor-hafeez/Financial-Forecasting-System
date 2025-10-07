"""
Financial AI Forecasting System - Main FastAPI Application

This module serves as the main entry point for the Financial AI Forecasting System,
providing RESTful API endpoints for data fetching, model training, forecasting,
and performance evaluation.

Key Features:
- Automated data fetching from external APIs (yfinance, Google RSS)
- Multiple forecasting models (ARIMA, LSTM, GRU, VAR, Moving Average, Ensemble)
- Real-time sentiment analysis from financial news
- Automated scheduling for data updates and model retraining
- Comprehensive model performance evaluation and comparison
- Interactive web interface for visualization and analysis

Architecture:
- FastAPI backend with MongoDB database
- React frontend with Material-UI components
- Plotly.js for interactive financial charts
- APScheduler for automated tasks
- TensorFlow/Keras for neural network models
- Statsmodels for traditional time series models

Author: Financial AI Team
Version: 1.0.0
License: MIT
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data_service import fetch_and_store, get_data
from models.forecast_service import ForecastService
from db_config import db
from services.scheduler_service import scheduler_service
from services.model_evaluator import model_evaluator
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Financial AI Forecasting System",
    description="Advanced financial market prediction using multiple AI models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize forecast service
forecast_service = ForecastService()

@app.get("/fetch-data/{symbol}")
def fetch_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch and store market data for a specific symbol.
    
    This endpoint fetches historical OHLCV data and sentiment data from external APIs,
    processes it with technical indicators, and stores it in MongoDB.
    
    Args:
        symbol (str): Financial instrument symbol (e.g., 'BTC-USD', 'AAPL', 'EURUSD=X')
        
    Returns:
        Dict[str, Any]: Response containing:
            - status: Success/failure status
            - message: Descriptive message
            - data_count: Number of records stored
            - symbol: The requested symbol
            
    Raises:
        HTTPException: If symbol is invalid or data fetching fails
        
    Example:
        GET /fetch-data/BTC-USD
        Response: {
            "status": "success",
            "message": "Data fetched and stored successfully",
            "data_count": 365,
            "symbol": "BTC-USD"
        }
    """
    try:
        logger.info(f"Fetching data for symbol: {symbol}")
        result = fetch_and_store(symbol)
        return result
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {symbol}: {str(e)}")

@app.get("/get-data/{symbol}")
def get_data_route(symbol: str):
    return get_data(symbol)

# Forecasting endpoints
@app.get("/forecast/moving-average/{symbol}")
def forecast_moving_average(symbol: str, steps: int = 24):
    return forecast_service.forecast_moving_average(symbol, steps)

@app.get("/forecast/arima/{symbol}")
def forecast_arima(symbol: str, steps: int = 24):
    return forecast_service.forecast_arima(symbol, steps)

@app.get("/forecast/var/{symbol}")
def forecast_var(symbol: str, steps: int = 24):
    return forecast_service.forecast_var(symbol, steps)

@app.get("/forecast/lstm/{symbol}")
def forecast_lstm(symbol: str, steps: int = 24):
    return forecast_service.forecast_lstm(symbol, steps)

@app.get("/forecast/gru/{symbol}")
def forecast_gru(symbol: str, steps: int = 24):
    return forecast_service.forecast_gru(symbol, steps)

@app.get("/forecast/ensemble/{symbol}")
def forecast_ensemble(symbol: str, steps: int = 24):
    return forecast_service.forecast_ensemble(symbol, steps)

@app.get("/models/performance/{symbol}")
def get_model_performance(symbol: str):
    return forecast_service.get_model_performance(symbol)

# New endpoints for frontend integration
@app.get("/get_instruments")
def get_instruments():
    """Returns list of available tickers from MongoDB"""
    try:
        # Get unique symbols from historical_data collection
        instruments = db.historical_data.distinct("Symbol")
        return {"instruments": instruments}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_historical/{symbol}")
def get_historical_data(symbol: str, limit: int = 100):
    """Returns OHLCV + indicator data for the selected symbol"""
    try:
        from data_service import get_data
        # Get more data points for historical chart
        prices = list(db.historical_data.find(
            {"Symbol": symbol}, 
            {"_id": 0}
        ).sort("Date", -1).limit(limit))
        
        # Convert datetime objects to ISO format
        from datetime import datetime
        import math
        
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                return None
            else:
                return obj
        
        prices = convert_datetime(prices)
        return {"symbol": symbol, "historical_data": prices}
    except Exception as e:
        return {"error": str(e)}

@app.get("/forecast/{symbol}")
def get_forecast(symbol: str, horizon: int = 24, model: str = "ensemble"):
    """Returns model predictions for given horizon and model"""
    try:
        # Get forecast based on selected model
        if model == "ensemble":
            result = forecast_service.forecast_ensemble(symbol, horizon)
        elif model == "lstm":
            result = forecast_service.forecast_lstm(symbol, horizon)
        elif model == "arima":
            result = forecast_service.forecast_arima(symbol, horizon)
        elif model == "moving_average":
            result = forecast_service.forecast_moving_average(symbol, horizon)
        elif model == "var":
            result = forecast_service.forecast_var(symbol, horizon)
        elif model == "gru":
            result = forecast_service.forecast_gru(symbol, horizon)
        else:
            # Default to ensemble if model not recognized
            result = forecast_service.forecast_ensemble(symbol, horizon)
        
        # Format response for frontend
        if "predictions" in result:
            predictions = []
            from datetime import datetime, timedelta
            base_time = datetime.now()
            
            for i, pred in enumerate(result["predictions"]):
                predictions.append({
                    "timestamp": (base_time + timedelta(hours=i)).isoformat() + "Z",
                    "value": float(pred)
                })
            
            return {
                "symbol": symbol,
                "model_used": result.get("model_name", model.title()),
                "predictions": predictions,
                "metrics": result.get("metrics", {})
            }
        else:
            return {"error": "No predictions available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection by checking if we can access collections
        db.historical_data.count_documents({})
        scheduler_status = scheduler_service.get_scheduler_status()
        return {
            "status": "healthy",
            "backend": "FastAPI running",
            "database": "MongoDB connected",
            "scheduler": scheduler_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Start scheduler when FastAPI starts"""
    logging.info("🚀 Starting Financial Forecasting API...")
    scheduler_service.start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler when FastAPI shuts down"""
    logging.info("🛑 Shutting down Financial Forecasting API...")
    scheduler_service.stop_scheduler()

# Scheduler management endpoints
@app.get("/scheduler/status")
def get_scheduler_status():
    """Get scheduler status and job information"""
    return scheduler_service.get_scheduler_status()

@app.post("/scheduler/trigger/{update_type}")
def trigger_manual_update(update_type: str):
    """Manually trigger updates (data, forecast, sentiment, models, or all)"""
    scheduler_service.trigger_manual_update(update_type)
    return {"message": f"Manual {update_type} update triggered"}

# Model evaluation endpoints
@app.get("/models/compare/{symbol}")
def compare_models(symbol: str):
    """Compare all models for a specific symbol"""
    return model_evaluator.compare_models(symbol)

@app.get("/models/compare")
def compare_all_models():
    """Compare all models across all symbols"""
    return model_evaluator.compare_models()

@app.get("/models/best/{symbol}")
def get_best_model(symbol: str, metric: str = "rmse"):
    """Get the best performing model for a symbol"""
    return model_evaluator.get_best_model(symbol, metric)

@app.get("/models/performance-summary/{symbol}")
def get_performance_summary(symbol: str):
    """Get performance summary for a symbol"""
    return model_evaluator.get_performance_summary(symbol)

@app.get("/models/performance-summary")
def get_all_performance_summary():
    """Get performance summary for all symbols"""
    return model_evaluator.get_performance_summary()

@app.get("/models/report/{symbol}")
def generate_performance_report(symbol: str):
    """Generate comprehensive performance report for a symbol"""
    return model_evaluator.generate_performance_report(symbol)

@app.get("/models/report")
def generate_all_performance_report():
    """Generate comprehensive performance report for all symbols"""
    return model_evaluator.generate_performance_report()
