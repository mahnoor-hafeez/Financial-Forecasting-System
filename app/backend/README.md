# Financial Forecasting Models - Part 2

This directory contains the implementation of multiple forecasting models for financial time series data, including traditional statistical models and neural network approaches.

## 📁 Structure

```
models/
├── arima_model.py          # ARIMA time series model
├── moving_average_model.py # Moving Average baseline model
├── var_model.py           # Vector Autoregression model
├── lstm_model.py          # Long Short-Term Memory neural network
├── gru_model.py           # Gated Recurrent Unit neural network
├── ensemble_model.py      # Ensemble combining multiple models
├── model_evaluator.py     # Model evaluation and metrics
├── forecast_service.py    # FastAPI service for model predictions
└── train_models.py        # Main training script

tests/
└── test_models.py         # Unit tests for all models
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Train Models

```bash
cd backend
python models/train_models.py
```

### 3. Run Tests

```bash
python -m pytest tests/test_models.py
```

## 📊 Models Implemented

### 1. Baseline Models

#### Moving Average Model
- **Purpose**: Simple baseline for trend estimation
- **Parameters**: `window_size` (default: 20)
- **Features**: Uses recent price history for predictions
- **Best for**: Short-term trend following

#### ARIMA Model
- **Purpose**: Autoregressive Integrated Moving Average
- **Parameters**: Auto-selected (p, d, q) using AIC
- **Features**: Handles non-stationary time series
- **Best for**: Univariate time series forecasting

#### VAR Model
- **Purpose**: Vector Autoregression for multivariate relationships
- **Parameters**: Auto-selected lag using information criteria
- **Features**: Considers relationships between Close, Volume, Daily_Return
- **Best for**: Multivariate time series with interdependencies

### 2. Neural Network Models

#### LSTM Model
- **Purpose**: Long Short-Term Memory for complex temporal patterns
- **Architecture**: 2-layer LSTM + Dense output
- **Parameters**:
  - `sequence_length`: 60 (input window)
  - `units`: 50 (LSTM units per layer)
  - `dropout`: 0.2 (regularization)
  - `epochs`: 50 (training iterations)
  - `batch_size`: 32 (training batch size)

#### GRU Model
- **Purpose**: Gated Recurrent Unit (simplified LSTM)
- **Architecture**: 2-layer GRU + Dense output
- **Parameters**: Same as LSTM
- **Best for**: Similar to LSTM but with fewer parameters

### 3. Ensemble Model
- **Purpose**: Combine multiple models for improved stability
- **Method**: Weighted average of predictions
- **Optimization**: Automatic weight optimization using validation data
- **Best for**: Reducing prediction variance

## 🔧 Model Parameters

### Default Hyperparameters

| Model | Key Parameters | Default Values |
|-------|---------------|----------------|
| Moving Average | window_size | 20 |
| ARIMA | (p,d,q) | Auto-selected |
| VAR | lag | Auto-selected |
| LSTM | sequence_length, units, epochs | 60, 50, 50 |
| GRU | sequence_length, units, epochs | 60, 50, 50 |
| Ensemble | weights | Auto-optimized |

### Feature Engineering
- **Input Features**: Close, Volume, Daily_Return, Volatility, SMA_7, SMA_14, EMA_7, EMA_14
- **Normalization**: MinMaxScaler for neural networks
- **Sequence Creation**: Sliding window approach for time series

## 📈 Evaluation Metrics

All models are evaluated using:
- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error
- **MAPE**: Mean Absolute Percentage Error

## 🗄️ Database Integration

### Collections Used
- `historical_data`: Market data and technical indicators
- `model_performance`: Model evaluation results and metrics

### Stored Information
- Model parameters and hyperparameters
- Evaluation metrics (RMSE, MAE, MAPE)
- Predictions and actual values
- Training timestamps

## 🌐 API Endpoints

### Forecasting Endpoints
- `GET /forecast/moving-average/{symbol}` - Moving Average predictions
- `GET /forecast/arima/{symbol}` - ARIMA predictions
- `GET /forecast/var/{symbol}` - VAR predictions
- `GET /forecast/lstm/{symbol}` - LSTM predictions
- `GET /forecast/gru/{symbol}` - GRU predictions
- `GET /forecast/ensemble/{symbol}` - Ensemble predictions

### Performance Endpoints
- `GET /models/performance/{symbol}` - Model performance metrics

### Response Format
```json
{
  "model": "LSTM",
  "symbol": "BTC-USD",
  "timestamp": "2025-10-04T00:00:00Z",
  "predictions": [100.5, 101.2, 102.1, ...],
  "steps": 24,
  "model_info": {...}
}
```

## 🧪 Testing

### Unit Tests
- Model training and prediction
- Evaluation metrics calculation
- Model save/load functionality
- Ensemble model combinations

### Run Tests
```bash
python -m pytest tests/test_models.py -v
```

## 📊 Performance Results

### Actual Performance (Latest Training Results)
- **BTC-USD**: Ensemble best (RMSE: 8,104.69), VAR working (RMSE: 10,413.04)
- **AAPL**: VAR best (RMSE: 18.92), all models working
- **EURUSD=X**: GRU best (RMSE: 0.0200), VAR failed (insufficient data)

### Model Performance Summary
- **Moving Average**: Consistent baseline performance across all symbols
- **ARIMA**: Working but high RMSE, needs further tuning
- **VAR**: Fixed and working (except EURUSD=X due to insufficient data)
- **LSTM/GRU**: Good performance, no reshape errors
- **Ensemble**: Best overall performance for BTC-USD

### Model Selection Guidelines
- **Short-term predictions (1-7 days)**: LSTM/GRU or Ensemble
- **Medium-term predictions (1-4 weeks)**: VAR or ARIMA
- **Trend following**: Moving Average
- **Maximum stability**: Ensemble

## 🔄 Training Workflow

1. **Data Loading**: Load historical data from MongoDB
2. **Data Splitting**: 80% train, 20% test
3. **Model Training**: Train each model type
4. **Model Evaluation**: Calculate metrics on test data
5. **Model Saving**: Save trained models to files
6. **Results Storage**: Store performance metrics in database

## 🚨 Error Handling

- **Insufficient Data**: Models require minimum data points
- **Missing Features**: Automatic handling of NaN values
- **Model Loading**: Graceful fallback if model files missing
- **API Errors**: Comprehensive error messages for debugging

## 📝 Logging

- Training progress and completion
- Model performance metrics
- Error messages and warnings
- Database operation status

## 🔧 Recent Updates (Model Tuning)

### Bug Fixes Applied
- **VAR Model**: Fixed `forecast()` method requiring last lag values as input
- **LSTM/GRU**: Fixed array reshaping errors with proper feature dimension handling
- **ARIMA**: Improved parameter selection with expanded grid search and common orders
- **Ensemble**: Added compatibility for different model `predict()` method signatures

### Performance Improvements
- **VAR**: Now working correctly for BTC-USD and AAPL (RMSE: 10,413 and 18.92)
- **LSTM/GRU**: No more reshape errors, proper sequence handling
- **Training Success**: 17/18 models trained and saved successfully
- **Model Evaluation**: All trained models evaluated with proper metrics

### Current Status
- ✅ All baseline models working (Moving Average, ARIMA, VAR)
- ✅ All neural models working (LSTM, GRU)
- ✅ Ensemble models working for all symbols
- ⚠️ ARIMA performance still needs tuning (high RMSE)
- ⚠️ VAR requires sufficient data (failed for EURUSD=X with 521 records)

## 🔮 Future Enhancements

- **ARIMA Tuning**: Further parameter optimization for better performance
- **Transformer Models**: Attention-based time series models
- **Sentiment Integration**: Incorporate news sentiment scores
- **Real-time Updates**: Streaming model updates
- **Hyperparameter Optimization**: Automated parameter tuning
- **Cross-validation**: More robust model evaluation
- **Feature Engineering**: Advanced technical indicators

## 📞 Support

For issues or questions:
1. Check the logs for error messages
2. Verify data availability in MongoDB
3. Ensure all dependencies are installed
4. Run unit tests to verify functionality
