# Financial AI Forecasting System - API Documentation

## Overview

The Financial AI Forecasting System provides a comprehensive REST API for financial market prediction using multiple machine learning models. The API is built with FastAPI and provides endpoints for data management, model training, forecasting, and performance evaluation.

## Base URL
```
http://127.0.0.1:8001
```

## Authentication
Currently, the API does not require authentication. In production, implement proper authentication mechanisms.

## API Endpoints

### 1. Data Management

#### Fetch Market Data
```http
GET /fetch-data/{symbol}
```

Fetches and stores historical market data for a specific symbol.

**Parameters:**
- `symbol` (string, required): Financial instrument symbol (e.g., 'BTC-USD', 'AAPL', 'EURUSD=X')

**Response:**
```json
{
  "status": "success",
  "message": "Data fetched and stored successfully",
  "data_count": 365,
  "symbol": "BTC-USD"
}
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:8001/fetch-data/BTC-USD"
```

#### Get Historical Data
```http
GET /get-data/{symbol}
```

Retrieves stored historical data for a symbol.

**Parameters:**
- `symbol` (string, required): Financial instrument symbol

**Response:**
```json
[
  {
    "Date": "2023-01-01T00:00:00",
    "Open": 16500.0,
    "High": 16800.0,
    "Low": 16200.0,
    "Close": 16650.0,
    "Volume": 25000000,
    "SMA_20": 16450.0,
    "EMA_20": 16520.0,
    "Daily_Return": 0.009,
    "Volatility": 0.025
  }
]
```

### 2. Forecasting Endpoints

#### Generate Forecast
```http
GET /forecast/{symbol}?horizon=24
```

Generates forecasts using the best performing model (ensemble).

**Parameters:**
- `symbol` (string, required): Financial instrument symbol
- `horizon` (integer, optional): Forecast horizon in hours (default: 24)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "timestamp": "2024-01-15T10:30:00",
  "model_used": "ensemble",
  "predictions": [
    {
      "timestamp": "2024-01-15T11:00:00",
      "value": 42500.0
    }
  ],
  "metrics": {
    "rmse": 1250.5,
    "mae": 980.2,
    "mape": 2.3
  }
}
```

#### Individual Model Forecasts

##### Moving Average Forecast
```http
GET /forecast/moving-average/{symbol}?steps=24
```

##### ARIMA Forecast
```http
GET /forecast/arima/{symbol}?steps=24
```

##### VAR Forecast
```http
GET /forecast/var/{symbol}?steps=24
```

##### LSTM Forecast
```http
GET /forecast/lstm/{symbol}?steps=24
```

##### GRU Forecast
```http
GET /forecast/gru/{symbol}?steps=24
```

### 3. Model Performance & Evaluation

#### Compare Models
```http
GET /models/compare/{symbol}
```

Compares performance of all models for a specific symbol.

**Response:**
```json
{
  "symbol": "BTC-USD",
  "comparison_date": "2024-01-15T10:30:00",
  "models": {
    "lstm": {
      "rmse": 1200.5,
      "mae": 950.2,
      "mape": 2.1,
      "performance_score": 85.5,
      "model_type": "Neural Network"
    }
  },
  "rankings": {
    "rmse": {
      "best": "lstm",
      "worst": "moving_average",
      "scores": {
        "lstm": 1200.5,
        "arima": 1350.2
      }
    }
  }
}
```

#### Get Best Model
```http
GET /models/best/{symbol}?metric=rmse
```

Returns the best performing model for a specific metric.

**Parameters:**
- `symbol` (string, required): Financial instrument symbol
- `metric` (string, optional): Performance metric ('rmse', 'mae', 'mape')

#### Performance Summary
```http
GET /models/performance-summary/{symbol}
```

Returns comprehensive performance summary for a symbol.

#### Generate Performance Report
```http
GET /models/report/{symbol}
```

Generates detailed performance report with recommendations.

### 4. Scheduler Management

#### Get Scheduler Status
```http
GET /scheduler/status
```

Returns current scheduler status and job information.

**Response:**
```json
{
  "status": "running",
  "jobs": [
    {
      "id": "daily_data_update",
      "name": "Daily Market Data Update",
      "next_run": "2024-01-16T06:00:00",
      "trigger": "cron[hour=6, minute=0]"
    }
  ],
  "total_jobs": 4
}
```

#### Trigger Manual Update
```http
POST /scheduler/trigger/{update_type}
```

Manually triggers updates for testing purposes.

**Parameters:**
- `update_type` (string, required): Type of update ('data', 'forecast', 'sentiment', 'models', 'all')

### 5. System Health

#### Health Check
```http
GET /health
```

Returns system health status including database connectivity and scheduler status.

**Response:**
```json
{
  "status": "healthy",
  "backend": "FastAPI running",
  "database": "MongoDB connected",
  "scheduler": {
    "status": "running",
    "total_jobs": 4
  }
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid symbol format"
}
```

#### 404 Not Found
```json
{
  "detail": "Symbol not found in database"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to fetch data for BTC-USD: Connection timeout"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting to prevent abuse.

## Data Models

### Market Data Schema
```json
{
  "Date": "ISO 8601 datetime",
  "Open": "float",
  "High": "float", 
  "Low": "float",
  "Close": "float",
  "Volume": "integer",
  "SMA_20": "float",
  "EMA_20": "float",
  "Daily_Return": "float",
  "Volatility": "float"
}
```

### Forecast Schema
```json
{
  "symbol": "string",
  "timestamp": "ISO 8601 datetime",
  "model_used": "string",
  "predictions": [
    {
      "timestamp": "ISO 8601 datetime",
      "value": "float"
    }
  ],
  "metrics": {
    "rmse": "float",
    "mae": "float", 
    "mape": "float"
  }
}
```

### Performance Metrics Schema
```json
{
  "symbol": "string",
  "model_name": "string",
  "timestamp": "ISO 8601 datetime",
  "metrics": {
    "rmse": "float",
    "mae": "float",
    "mape": "float"
  },
  "model_params": "object"
}
```

## Usage Examples

### Python Client Example
```python
import requests
import json

# Fetch data for Bitcoin
response = requests.get("http://127.0.0.1:8001/fetch-data/BTC-USD")
data = response.json()
print(f"Fetched {data['data_count']} records for {data['symbol']}")

# Generate forecast
forecast = requests.get("http://127.0.0.1:8001/forecast/BTC-USD?horizon=24")
predictions = forecast.json()
print(f"Next price prediction: ${predictions['predictions'][0]['value']:.2f}")

# Compare models
comparison = requests.get("http://127.0.0.1:8001/models/compare/BTC-USD")
models = comparison.json()
print(f"Best model: {models['rankings']['rmse']['best']}")
```

### JavaScript Client Example
```javascript
// Fetch data
const fetchData = async (symbol) => {
  const response = await fetch(`http://127.0.0.1:8001/fetch-data/${symbol}`);
  return await response.json();
};

// Generate forecast
const generateForecast = async (symbol, horizon = 24) => {
  const response = await fetch(`http://127.0.0.1:8001/forecast/${symbol}?horizon=${horizon}`);
  return await response.json();
};

// Compare models
const compareModels = async (symbol) => {
  const response = await fetch(`http://127.0.0.1:8001/models/compare/${symbol}`);
  return await response.json();
};

// Usage
fetchData('BTC-USD').then(data => console.log(data));
generateForecast('BTC-USD', 24).then(forecast => console.log(forecast));
compareModels('BTC-USD').then(comparison => console.log(comparison));
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

These provide interactive interfaces to test API endpoints directly from the browser.

## WebSocket Support

Currently, the API does not support WebSocket connections. For real-time updates, implement WebSocket endpoints for live data streaming.

## Versioning

The API is currently at version 1.0.0. Future versions will be available at `/v2/`, `/v3/`, etc.

## Support

For technical support or questions about the API, please refer to the project documentation or contact the development team.
