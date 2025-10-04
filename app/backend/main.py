from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_service import fetch_and_store, get_data
from models.forecast_service import ForecastService

app = FastAPI(title="Financial Forecasting API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
