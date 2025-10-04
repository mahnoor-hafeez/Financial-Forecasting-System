import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class ARIMAForecaster:
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.params = {}
        
    def check_stationarity(self, series):
        """Check if series is stationary using Augmented Dickey-Fuller test"""
        result = adfuller(series.dropna())
        return result[1] < 0.05  # p-value < 0.05 means stationary
    
    def make_stationary(self, series):
        """Make series stationary by differencing"""
        diff_series = series.diff().dropna()
        return diff_series
    
    def find_best_params(self, series, max_p=3, max_d=2, max_q=3):
        """Find best ARIMA parameters using AIC"""
        best_aic = np.inf
        best_params = (0, 0, 0)
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_params = (p, d, q)
                    except:
                        continue
                        
        return best_params, best_aic
    
    def train(self, data, target_column='Close'):
        """Train ARIMA model"""
        series = data[target_column].dropna()
        
        # Check stationarity
        if not self.check_stationarity(series):
            series = self.make_stationary(series)
            self.params['differenced'] = True
        else:
            self.params['differenced'] = False
            
        # Find best parameters
        best_params, best_aic = self.find_best_params(series)
        self.params['order'] = best_params
        self.params['aic'] = best_aic
        
        # Train model
        self.model = ARIMA(series, order=best_params)
        self.fitted_model = self.model.fit()
        
        return self
    
    def predict(self, data=None, steps=24):
        """Make predictions"""
        if self.fitted_model is None:
            raise ValueError("Model must be trained first")
            
        forecast = self.fitted_model.forecast(steps=steps)
        return forecast
    
    def evaluate(self, test_data, target_column='Close'):
        """Evaluate model performance"""
        predictions = self.predict(steps=len(test_data))
        actual = test_data[target_column].values
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(actual, predictions))
        mae = mean_absolute_error(actual, predictions)
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        return {
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'predictions': predictions.tolist(),
            'actual': actual.tolist()
        }
    
    def get_model_info(self):
        """Get model parameters and summary"""
        if self.fitted_model is None:
            return "Model not trained"
            
        return {
            'model_type': 'ARIMA',
            'order': self.params['order'],
            'aic': self.params['aic'],
            'differenced': self.params['differenced'],
            'summary': self.fitted_model.summary().as_text()
        }
