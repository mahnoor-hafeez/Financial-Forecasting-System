import pandas as pd
import numpy as np
from datetime import datetime
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

# Import models
from arima_model import ARIMAForecaster
from moving_average_model import MovingAverageForecaster
from var_model import VARForecaster
from lstm_model import LSTMForecaster
from gru_model import GRUForecaster
from ensemble_model import EnsembleForecaster

# Import database connection
from db_config import db

class ForecastService:
    def __init__(self):
        self.models = {}
        self.models_dir = "models"
        
    def load_data(self, symbol):
        """Load data from MongoDB for a symbol"""
        try:
            cursor = db.historical_data.find({'Symbol': symbol}).sort('Date', 1)
            data = pd.DataFrame(list(cursor))
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
                
            # Convert Date column
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
            data.sort_index(inplace=True)
            
            return data
            
        except Exception as e:
            raise ValueError(f"Error loading data for {symbol}: {str(e)}")
    
    def load_model(self, symbol, model_name):
        """Load a trained model from file"""
        model_path = f"{self.models_dir}/{symbol}/{model_name.lower()}_model"
        
        try:
            # Try loading as neural model first (.h5)
            if os.path.exists(f"{model_path}.h5"):
                if model_name.lower() == 'lstm':
                    model = LSTMForecaster()
                elif model_name.lower() == 'gru':
                    model = GRUForecaster()
                else:
                    raise ValueError(f"Unknown neural model: {model_name}")
                
                model.load_model(f"{model_path}.h5")
                return model
            
            # Try loading as pickle file
            elif os.path.exists(f"{model_path}.pkl"):
                with open(f"{model_path}.pkl", 'rb') as f:
                    return pickle.load(f)
            
            else:
                raise FileNotFoundError(f"Model file not found: {model_path}")
                
        except Exception as e:
            raise ValueError(f"Error loading {model_name} model for {symbol}: {str(e)}")
    
    def forecast_moving_average(self, symbol, steps=24):
        """Forecast using Moving Average model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'MovingAverage')
            
            predictions = model.predict(steps)
            
            return {
                "model": "Moving Average",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def forecast_arima(self, symbol, steps=24):
        """Forecast using ARIMA model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'ARIMA')
            
            predictions = model.predict(steps)
            
            return {
                "model": "ARIMA",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def forecast_var(self, symbol, steps=24):
        """Forecast using VAR model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'VAR')
            
            predictions = model.predict(steps)
            
            return {
                "model": "VAR",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def forecast_lstm(self, symbol, steps=24):
        """Forecast using LSTM model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'LSTM')
            
            predictions = model.predict(data, steps)
            
            return {
                "model": "LSTM",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def forecast_gru(self, symbol, steps=24):
        """Forecast using GRU model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'GRU')
            
            predictions = model.predict(data, steps)
            
            return {
                "model": "GRU",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def forecast_ensemble(self, symbol, steps=24):
        """Forecast using Ensemble model"""
        try:
            data = self.load_data(symbol)
            model = self.load_model(symbol, 'Ensemble')
            
            predictions = model.predict(data, steps)
            
            return {
                "model": "Ensemble",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "steps": steps,
                "model_info": model.get_model_info()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_model_performance(self, symbol):
        """Get model performance metrics from database"""
        try:
            # Get performance data from MongoDB
            cursor = db.model_performance.find({'symbol': symbol}).sort('timestamp', -1)
            performance_data = list(cursor)
            
            if not performance_data:
                return {"error": f"No performance data found for {symbol}"}
            
            # Group by model name and get latest performance
            model_performance = {}
            for record in performance_data:
                model_name = record['model_name']
                if model_name not in model_performance:
                    model_performance[model_name] = {
                        'metrics': record['metrics'],
                        'timestamp': record['timestamp'],
                        'model_params': record.get('model_params', {})
                    }
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "model_performance": model_performance
            }
            
        except Exception as e:
            return {"error": str(e)}
