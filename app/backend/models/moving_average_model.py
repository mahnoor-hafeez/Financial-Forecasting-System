import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

class MovingAverageForecaster:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.trained_data = None
        self.params = {'window_size': window_size}
        
    def train(self, data, target_column='Close'):
        """Train moving average model (just store the data)"""
        self.trained_data = data[target_column].dropna()
        return self
    
    def predict(self, data=None, steps=24):
        """Make predictions using moving average"""
        if self.trained_data is None:
            raise ValueError("Model must be trained first")
            
        # Use the last window_size values to calculate moving average
        last_values = self.trained_data.tail(self.window_size)
        ma_value = last_values.mean()
        
        # Return the same value for all prediction steps
        predictions = np.full(steps, ma_value)
        return predictions
    
    def predict_with_trend(self, data=None, steps=24):
        """Make predictions with trend consideration"""
        if self.trained_data is None:
            raise ValueError("Model must be trained first")
            
        # Calculate recent trend
        recent_data = self.trained_data.tail(self.window_size)
        if len(recent_data) >= 2:
            trend = (recent_data.iloc[-1] - recent_data.iloc[0]) / len(recent_data)
        else:
            trend = 0
            
        # Start with the last known value
        predictions = []
        last_value = recent_data.iloc[-1]
        
        for i in range(steps):
            predicted_value = last_value + (trend * (i + 1))
            predictions.append(predicted_value)
            
        return np.array(predictions)
    
    def evaluate(self, test_data, target_column='Close', use_trend=True):
        """Evaluate model performance"""
        if use_trend:
            predictions = self.predict_with_trend(steps=len(test_data))
        else:
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
            'actual': actual.tolist(),
            'use_trend': use_trend
        }
    
    def get_model_info(self):
        """Get model parameters"""
        return {
            'model_type': 'Moving Average',
            'window_size': self.params['window_size'],
            'data_length': len(self.trained_data) if self.trained_data is not None else 0
        }
