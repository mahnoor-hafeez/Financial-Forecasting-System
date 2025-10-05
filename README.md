# 📈 Financial AI Pro - Complete Trading Platform

A comprehensive financial forecasting system combining traditional statistical models with advanced neural networks, integrated with a modern web interface for real-time market analysis and prediction.

## 🚀 Project Overview

This project implements a complete financial analysis and forecasting platform with three main components:

### Part 1: Data Pipeline + FastAPI + MongoDB + React
- **Data Collection**: Historical OHLCV data via Yahoo Finance API
- **Technical Analysis**: SMA, EMA, Daily Return, Volatility calculations
- **Sentiment Analysis**: Real-time financial news sentiment via Google RSS
- **Database Storage**: MongoDB with time-series collections
- **API Layer**: FastAPI with CORS support
- **Frontend**: React interface for data visualization

### Part 2: Forecasting Models (Traditional + Neural)
- **Traditional Models**: Moving Average, ARIMA, VAR
- **Neural Networks**: LSTM, GRU models
- **Ensemble Methods**: Weighted combination of predictions
- **Model Evaluation**: RMSE, MAE, MAPE metrics
- **Model Persistence**: Saved models (.h5, .pkl files)

### Part 3: Web Application (Frontend + Backend Integration)
- **Professional UI**: Dark theme financial dashboard
- **Interactive Charts**: Candlestick charts with AI predictions
- **Real-time Data**: Live market data with sentiment analysis
- **Model Performance**: Metrics display and comparison
- **Responsive Design**: Mobile-friendly interface

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for time-series data
- **Python Libraries**:
  - `yfinance`: Market data fetching
  - `pandas`: Data manipulation
  - `numpy`: Numerical computing
  - `statsmodels`: Statistical models (ARIMA, VAR)
  - `tensorflow/keras`: Neural networks (LSTM, GRU)
  - `scikit-learn`: Machine learning utilities
  - `textblob`: Sentiment analysis
  - `ta`: Technical analysis indicators

### Frontend
- **React 18**: Modern JavaScript framework
- **Material-UI**: Professional UI components
- **Plotly.js**: Interactive financial charts
- **Axios**: HTTP client for API communication
- **Moment.js**: Date/time manipulation

### Database
- **MongoDB**: Document-based storage
- **Collections**:
  - `historical_data`: OHLCV + technical indicators
  - `sentiments`: News sentiment analysis
  - `model_performance`: Model evaluation metrics

## 📁 Project Structure

```
NLP-A2/
├── app/
│   ├── backend/
│   │   ├── main.py                 # FastAPI application
│   │   ├── data_service.py         # Data fetching and storage
│   │   ├── db_config.py           # MongoDB configuration
│   │   ├── requirements.txt       # Python dependencies
│   │   ├── models/                # Forecasting models
│   │   │   ├── arima_model.py
│   │   │   ├── lstm_model.py
│   │   │   ├── gru_model.py
│   │   │   ├── var_model.py
│   │   │   ├── moving_average_model.py
│   │   │   ├── ensemble_model.py
│   │   │   ├── forecast_service.py
│   │   │   └── model_evaluator.py
│   │   ├── tests/                 # Unit tests
│   │   └── README.md              # Backend documentation
│   └── frontend/
│       ├── package.json           # Node.js dependencies
│       ├── src/
│       │   ├── App.jsx            # Main React component
│       │   ├── components/        # React components
│       │   │   ├── ForecastChart.jsx
│       │   │   ├── MetricsPanel.jsx
│       │   │   ├── Loader.jsx
│       │   │   └── ErrorAlert.jsx
│       │   └── services/
│       │       └── api.js         # API communication
│       └── public/
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NLP-A2
   ```

2. **Set up Python environment**
   ```bash
   cd app/backend
   pip install -r requirements.txt
   ```

3. **Configure MongoDB**
   - Install MongoDB
   - Create `.env` file with your MongoDB connection string
   ```env
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=financial_forecasting
   ```

4. **Start the backend server**
   ```bash
   cd app/backend
   python -m uvicorn main:app --port 8001 --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd app/frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## 📊 Features

### Data Pipeline
- ✅ Real-time market data fetching
- ✅ Technical indicator calculations
- ✅ News sentiment analysis
- ✅ MongoDB time-series storage

### Forecasting Models
- ✅ **Moving Average**: Simple trend following
- ✅ **ARIMA**: Auto-regressive integrated moving average
- ✅ **VAR**: Vector autoregression for multivariate analysis
- ✅ **LSTM**: Long short-term memory neural network
- ✅ **GRU**: Gated recurrent unit neural network
- ✅ **Ensemble**: Weighted combination of all models

### Web Interface
- ✅ **Professional Dashboard**: Dark theme financial interface
- ✅ **Interactive Charts**: Candlestick charts with predictions
- ✅ **Real-time Updates**: Live market data and sentiment
- ✅ **Model Metrics**: Performance comparison and analysis
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Error Handling**: Graceful error management

### API Endpoints

#### Data Endpoints
- `GET /get_instruments` - List available trading instruments
- `GET /get_historical/{symbol}` - Historical OHLCV data
- `GET /fetch-data/{symbol}` - Fetch and store new data
- `GET /get-data/{symbol}` - Sample data for testing

#### Forecasting Endpoints
- `GET /forecast/{symbol}` - Ensemble forecast (recommended)
- `GET /forecast/moving-average/{symbol}` - Moving average forecast
- `GET /forecast/arima/{symbol}` - ARIMA model forecast
- `GET /forecast/var/{symbol}` - VAR model forecast
- `GET /forecast/lstm/{symbol}` - LSTM neural network forecast
- `GET /forecast/gru/{symbol}` - GRU neural network forecast
- `GET /forecast/ensemble/{symbol}` - Ensemble model forecast

#### Utility Endpoints
- `GET /models/performance/{symbol}` - Model performance metrics
- `GET /health` - System health check

## 🎯 Usage Examples

### Generate a Forecast
1. Select an instrument from the dropdown
2. Choose forecast horizon (1-72 hours)
3. Select data range (100-1000 days)
4. Click "Generate Forecast"
5. View results in interactive chart

### API Usage
```bash
# Get available instruments
curl http://localhost:8001/get_instruments

# Get historical data
curl "http://localhost:8001/get_historical/BTC-USD?limit=100"

# Generate forecast
curl "http://localhost:8001/forecast/BTC-USD?horizon=24"

# Check system health
curl http://localhost:8001/health
```

## 🔧 Configuration

### Environment Variables
```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=financial_forecasting

# API Configuration
API_HOST=127.0.0.1
API_PORT=8001

# Frontend Configuration
REACT_APP_API_URL=http://127.0.0.1:8001
```

### Model Parameters
- **ARIMA**: Auto-tuned (p,d,q) parameters
- **LSTM/GRU**: 60-sequence length, 2 layers
- **VAR**: 2-lag vector autoregression
- **Moving Average**: 20-period window

## 📈 Model Performance

### Evaluation Metrics
- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error
- **MAPE**: Mean Absolute Percentage Error

### Current Performance (Sample)
- **BTC-USD**: Ensemble RMSE ~150-200
- **AAPL**: Ensemble RMSE ~18-25
- **EURUSD=X**: Ensemble RMSE ~0.002-0.005

## 🚀 Recent Updates (Part 3)

### Frontend + Backend Integration
- ✅ **Professional UI**: Dark theme financial dashboard
- ✅ **Interactive Charts**: Plotly.js candlestick charts
- ✅ **Real-time Data**: Live market data integration
- ✅ **Model Metrics**: Performance display panel
- ✅ **Responsive Design**: Mobile-friendly interface
- ✅ **Error Handling**: Graceful error management

### Chart Features
- ✅ **Candlestick Charts**: Green/red for bullish/bearish
- ✅ **AI Forecast Overlay**: Gold dotted prediction line
- ✅ **Interactive Tooltips**: Hover for detailed information
- ✅ **Professional Styling**: Financial-grade appearance
- ✅ **Real-time Updates**: Dynamic data loading

### Technical Improvements
- ✅ **CORS Configuration**: Proper cross-origin support
- ✅ **Data Serialization**: JSON-compatible datetime handling
- ✅ **Error Boundaries**: React error handling
- ✅ **Loading States**: Professional loading indicators
- ✅ **API Integration**: Seamless frontend-backend communication

## 🧪 Testing

### Backend Tests
```bash
cd app/backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd app/frontend
npm test
```

### API Testing
```bash
# Health check
curl http://localhost:8001/health

# Test all endpoints
curl http://localhost:8001/get_instruments
curl "http://localhost:8001/get_historical/BTC-USD?limit=10"
curl "http://localhost:8001/forecast/BTC-USD?horizon=24"
```

## 📝 Development Notes

### Model Training
- Models are pre-trained and saved in `/models/{symbol}/`
- Training can be re-run using `train_models.py`
- Model evaluation stored in MongoDB `model_performance` collection

### Data Flow
1. **Data Collection**: yfinance → MongoDB
2. **Model Training**: Historical data → Model files
3. **Prediction**: Live data → Forecast service → API
4. **Visualization**: API → React → Charts

### Performance Optimization
- **Caching**: Model predictions cached in memory
- **Async Processing**: Non-blocking API endpoints
- **Data Pagination**: Configurable data limits
- **Error Recovery**: Graceful fallbacks for failed models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Yahoo Finance**: Market data provider
- **Google News**: Sentiment analysis data source
- **Plotly.js**: Interactive charting library
- **Material-UI**: React component library
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed description
4. Include error logs and system information

---

**Financial AI Pro** - Advanced Market Prediction Engine
*Part 3: Frontend + Backend Integration Complete* ✅
