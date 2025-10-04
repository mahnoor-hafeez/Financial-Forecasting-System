import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

class EnsembleForecaster:
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.is_trained = False
        
    def add_model(self, name, model, weight=1.0):
        """Add a model to the ensemble"""
        self.models[name] = model
        self.weights[name] = weight
        
    def set_weights(self, weights):
        """Set weights for ensemble models"""
        if set(weights.keys()) != set(self.models.keys()):
            raise ValueError("Weight keys must match model names")
        self.weights = weights
        
    def normalize_weights(self):
        """Normalize weights to sum to 1"""
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v/total_weight for k, v in self.weights.items()}
    
    def predict(self, data, steps=24):
        """Make ensemble predictions"""
        if not self.models:
            raise ValueError("No models added to ensemble")
            
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            try:
                # Try with data parameter first, then without
                try:
                    pred = model.predict(data, steps)
                except TypeError:
                    pred = model.predict(steps=steps)
                predictions[name] = pred
            except Exception as e:
                print(f"Error getting predictions from {name}: {str(e)}")
                continue
        
        if not predictions:
            raise ValueError("No valid predictions from any model")
            
        # Calculate weighted average
        ensemble_pred = np.zeros(steps)
        total_weight = 0
        
        for name, pred in predictions.items():
            weight = self.weights.get(name, 1.0)
            if len(pred) >= steps:
                ensemble_pred += weight * pred[:steps]
                total_weight += weight
            else:
                # Pad with last value if prediction is shorter
                padded_pred = np.pad(pred, (0, steps - len(pred)), mode='edge')
                ensemble_pred += weight * padded_pred
                total_weight += weight
        
        if total_weight > 0:
            ensemble_pred /= total_weight
            
        return ensemble_pred
    
    def evaluate(self, test_data, target_column='Close'):
        """Evaluate ensemble performance"""
        predictions = self.predict(test_data, len(test_data))
        actual = test_data[target_column].values
        
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
    
    def optimize_weights(self, validation_data, target_column='Close'):
        """Optimize ensemble weights using validation data"""
        if not self.models:
            raise ValueError("No models added to ensemble")
            
        # Get predictions from all models
        model_predictions = {}
        for name, model in self.models.items():
            try:
                # Try with data parameter first, then without
                try:
                    pred = model.predict(validation_data, len(validation_data))
                except TypeError:
                    pred = model.predict(steps=len(validation_data))
                model_predictions[name] = pred
            except Exception as e:
                print(f"Error getting predictions from {name}: {str(e)}")
                continue
        
        if not model_predictions:
            raise ValueError("No valid predictions from any model")
            
        actual = validation_data[target_column].values
        
        # Simple optimization: find weights that minimize RMSE
        from scipy.optimize import minimize
        
        def objective(weights):
            # Normalize weights
            weights = weights / np.sum(weights)
            
            # Calculate ensemble prediction
            ensemble_pred = np.zeros(len(actual))
            for i, (name, pred) in enumerate(model_predictions.items()):
                if len(pred) >= len(actual):
                    ensemble_pred += weights[i] * pred[:len(actual)]
                else:
                    padded_pred = np.pad(pred, (0, len(actual) - len(pred)), mode='edge')
                    ensemble_pred += weights[i] * padded_pred
            
            # Calculate RMSE
            rmse = np.sqrt(np.mean((actual - ensemble_pred) ** 2))
            return rmse
        
        # Initial weights (equal)
        initial_weights = np.ones(len(model_predictions)) / len(model_predictions)
        
        # Optimize
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=[(0, 1) for _ in range(len(model_predictions))])
        
        # Update weights
        optimized_weights = result.x / np.sum(result.x)
        for i, name in enumerate(model_predictions.keys()):
            self.weights[name] = optimized_weights[i]
            
        return self.weights
    
    def get_model_info(self):
        """Get ensemble information"""
        return {
            'model_type': 'Ensemble',
            'models': list(self.models.keys()),
            'weights': self.weights,
            'model_count': len(self.models)
        }
