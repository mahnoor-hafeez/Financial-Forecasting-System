import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.var_model import VAR
try:
    from statsmodels.tsa.vector_ar.select_order import select_order
except ImportError:
    try:
        # Fallback for newer statsmodels versions
        from statsmodels.tsa.vector_ar.model import select_order
    except ImportError:
        # Manual implementation if select_order not available
        def select_order(data, maxlags=10):
            class LagSelection:
                def __init__(self, aic):
                    self.aic = aic
            return LagSelection(1)  # Default to lag 1
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class VARForecaster:
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.params = {}
        self.feature_columns = ['Close', 'Volume', 'Daily_Return']
        
    def prepare_data(self, data):
        """Prepare data for VAR model"""
        # Select relevant columns
        var_data = data[self.feature_columns].copy()
        
        # Handle missing values
        var_data = var_data.dropna()
        
        # Ensure all columns are numeric
        for col in var_data.columns:
            var_data[col] = pd.to_numeric(var_data[col], errors='coerce')
            
        var_data = var_data.dropna()
        
        return var_data
    
    def select_optimal_lag(self, data):
        """Select optimal lag order using information criteria"""
        try:
            lag_selection = select_order(data, maxlags=10)
            # Use AIC criterion
            optimal_lag = lag_selection.aic
            return optimal_lag
        except:
            # Default to lag 1 if selection fails
            return 1
    
    def train(self, data):
        """Train VAR model"""
        # Prepare data
        var_data = self.prepare_data(data)
        
        if len(var_data) < 50:  # Need sufficient data for VAR
            raise ValueError("Insufficient data for VAR model. Need at least 50 observations.")
        
        # Select optimal lag
        optimal_lag = self.select_optimal_lag(var_data)
        self.params['lag'] = optimal_lag
        
        # Create and fit VAR model
        self.model = VAR(var_data)
        self.fitted_model = self.model.fit(maxlags=optimal_lag, ic='aic')
        
        return self
    
    def predict(self, data=None, steps=24):
        """Make predictions"""
        if self.fitted_model is None:
            raise ValueError("Model must be trained first")
            
        # Get forecast for all variables
        forecast = self.fitted_model.forecast(steps=steps)
        
        # Return only Close price predictions (assuming it's the first column)
        close_predictions = forecast[:, 0]  # Close is first column
        return close_predictions
    
    def evaluate(self, test_data):
        """Evaluate model performance"""
        predictions = self.predict(steps=len(test_data))
        actual = test_data['Close'].values
        
        # Ensure same length
        min_length = min(len(predictions), len(actual))
        predictions = predictions[:min_length]
        actual = actual[:min_length]
        
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
            'model_type': 'VAR',
            'lag': self.params['lag'],
            'features': self.feature_columns,
            'summary': str(self.fitted_model.summary())
        }
