import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import db
import json

class ModelEvaluator:
    def __init__(self):
        self.results = []
        
    def calculate_metrics(self, actual, predictions):
        """Calculate evaluation metrics"""
        # Ensure same length
        min_length = min(len(actual), len(predictions))
        actual = actual[:min_length]
        predictions = predictions[:min_length]
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((actual - predictions) ** 2))
        mae = np.mean(np.abs(actual - predictions))
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape)
        }
    
    def evaluate_model(self, model, test_data, model_name, model_params, target_column='Close'):
        """Evaluate a single model"""
        try:
            # Get predictions - try different method signatures
            try:
                predictions = model.predict(test_data, len(test_data))
            except TypeError:
                try:
                    predictions = model.predict(steps=len(test_data))
                except TypeError:
                    predictions = model.predict(len(test_data))
            actual = test_data[target_column].values
            
            # Calculate metrics
            metrics = self.calculate_metrics(actual, predictions)
            
            # Create result record
            result = {
                'model_name': model_name,
                'model_params': model_params,
                'metrics': metrics,
                'timestamp': datetime.now(),
                'test_data_length': len(test_data),
                'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                'actual': actual.tolist() if hasattr(actual, 'tolist') else list(actual)
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"Error evaluating {model_name}: {str(e)}")
            return None
    
    def save_results_to_db(self, symbol):
        """Save evaluation results to MongoDB"""
        try:
            # Prepare results for database
            db_results = []
            for result in self.results:
                db_result = result.copy()
                db_result['symbol'] = symbol
                db_result['timestamp'] = db_result['timestamp'].isoformat()
                db_results.append(db_result)
            
            # Insert into MongoDB
            if db_results:
                db.model_performance.insert_many(db_results)
                print(f"Saved {len(db_results)} model evaluation results to database")
                
        except Exception as e:
            print(f"Error saving results to database: {str(e)}")
    
    def get_best_model(self, metric='rmse'):
        """Get the best performing model based on specified metric"""
        if not self.results:
            return None
            
        # Sort by metric (lower is better for rmse, mae, mape)
        sorted_results = sorted(self.results, key=lambda x: x['metrics'][metric])
        return sorted_results[0]
    
    def compare_models(self):
        """Compare all models and return summary"""
        if not self.results:
            return "No results to compare"
            
        comparison = []
        for result in self.results:
            comparison.append({
                'model_name': result['model_name'],
                'rmse': result['metrics']['rmse'],
                'mae': result['metrics']['mae'],
                'mape': result['metrics']['mape']
            })
            
        return pd.DataFrame(comparison)
    
    def get_results_summary(self):
        """Get summary of all evaluation results"""
        if not self.results:
            return "No results available"
            
        summary = {
            'total_models': len(self.results),
            'models': [r['model_name'] for r in self.results],
            'best_rmse': min(r['metrics']['rmse'] for r in self.results),
            'best_mae': min(r['metrics']['mae'] for r in self.results),
            'best_mape': min(r['metrics']['mape'] for r in self.results)
        }
        
        return summary
