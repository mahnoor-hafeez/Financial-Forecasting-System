from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_service import fetch_and_store, get_data
from models.forecast_service import ForecastService
from db_config import db

app = FastAPI(title="Financial Forecasting API")

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
def fetch_data(symbol: str):
    return fetch_and_store(symbol)

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
def get_forecast(symbol: str, horizon: int = 24):
    """Returns model predictions for given horizon"""
    try:
        # Get ensemble forecast (best performing model)
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
                "model_used": result.get("model_name", "Ensemble"),
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
        return {
            "status": "healthy",
            "backend": "FastAPI running",
            "database": "MongoDB connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
