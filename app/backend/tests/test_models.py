import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

from arima_model import ARIMAForecaster
from moving_average_model import MovingAverageForecaster
from var_model import VARForecaster
from lstm_model import LSTMForecaster
from gru_model import GRUForecaster
from ensemble_model import EnsembleForecaster
from model_evaluator import ModelEvaluator

class TestModels(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create synthetic test data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Generate synthetic price data
        price = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        volume = np.random.randint(1000, 10000, len(dates))
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Close': price,
            'Volume': volume,
            'Daily_Return': np.random.randn(len(dates)) * 0.02,
            'Volatility': np.random.randn(len(dates)) * 0.01,
            'SMA_7': price + np.random.randn(len(dates)) * 0.1,
            'SMA_14': price + np.random.randn(len(dates)) * 0.1,
            'EMA_7': price + np.random.randn(len(dates)) * 0.1,
            'EMA_14': price + np.random.randn(len(dates)) * 0.1
        })
        
        # Split into train and test
        split_idx = int(len(self.test_data) * 0.8)
        self.train_data = self.test_data.iloc[:split_idx]
        self.test_data = self.test_data.iloc[split_idx:]
        
    def test_moving_average_model(self):
        """Test Moving Average model"""
        model = MovingAverageForecaster(window_size=20)
        model.train(self.train_data)
        
        # Test prediction
        predictions = model.predict(steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = model.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = model.get_model_info()
        self.assertEqual(info['model_type'], 'Moving Average')
        
    def test_arima_model(self):
        """Test ARIMA model"""
        model = ARIMAForecaster()
        model.train(self.train_data)
        
        # Test prediction
        predictions = model.predict(steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = model.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = model.get_model_info()
        self.assertEqual(info['model_type'], 'ARIMA')
        
    def test_var_model(self):
        """Test VAR model"""
        model = VARForecaster()
        model.train(self.train_data)
        
        # Test prediction
        predictions = model.predict(steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = model.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = model.get_model_info()
        self.assertEqual(info['model_type'], 'VAR')
        
    def test_lstm_model(self):
        """Test LSTM model"""
        # Skip if not enough data
        if len(self.train_data) < 100:
            self.skipTest("Insufficient data for LSTM model")
            
        model = LSTMForecaster(sequence_length=30, epochs=5, batch_size=16)
        model.train(self.train_data)
        
        # Test prediction
        predictions = model.predict(self.train_data, steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = model.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = model.get_model_info()
        self.assertEqual(info['model_type'], 'LSTM')
        
    def test_gru_model(self):
        """Test GRU model"""
        # Skip if not enough data
        if len(self.train_data) < 100:
            self.skipTest("Insufficient data for GRU model")
            
        model = GRUForecaster(sequence_length=30, epochs=5, batch_size=16)
        model.train(self.train_data)
        
        # Test prediction
        predictions = model.predict(self.train_data, steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = model.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = model.get_model_info()
        self.assertEqual(info['model_type'], 'GRU')
        
    def test_ensemble_model(self):
        """Test Ensemble model"""
        # Create individual models
        ma_model = MovingAverageForecaster(window_size=20)
        ma_model.train(self.train_data)
        
        # Create ensemble
        ensemble = EnsembleForecaster()
        ensemble.add_model('MovingAverage', ma_model, weight=1.0)
        
        # Test prediction
        predictions = ensemble.predict(self.test_data, steps=10)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
        
        # Test evaluation
        metrics = ensemble.evaluate(self.test_data)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        
        # Test model info
        info = ensemble.get_model_info()
        self.assertEqual(info['model_type'], 'Ensemble')
        
    def test_model_evaluator(self):
        """Test Model Evaluator"""
        evaluator = ModelEvaluator()
        
        # Create test model
        model = MovingAverageForecaster(window_size=20)
        model.train(self.train_data)
        
        # Evaluate model
        result = evaluator.evaluate_model(
            model, self.test_data, 'TestModel', {'window_size': 20}
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['model_name'], 'TestModel')
        self.assertIn('metrics', result)
        self.assertIn('predictions', result)
        self.assertIn('actual', result)
        
        # Test comparison
        comparison = evaluator.compare_models()
        self.assertIsInstance(comparison, pd.DataFrame)
        
        # Test best model
        best_model = evaluator.get_best_model('rmse')
        self.assertIsNotNone(best_model)
        
    def test_model_save_load(self):
        """Test model save and load functionality"""
        # Test Moving Average model (pickle)
        model = MovingAverageForecaster(window_size=20)
        model.train(self.train_data)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            import pickle
            with open(tmp.name, 'wb') as f:
                pickle.dump(model, f)
            
            # Load model
            with open(tmp.name, 'rb') as f:
                loaded_model = pickle.load(f)
            
            # Test that loaded model works
            predictions = loaded_model.predict(steps=5)
            self.assertEqual(len(predictions), 5)
            
            # Clean up
            os.unlink(tmp.name)

if __name__ == '__main__':
    unittest.main()
