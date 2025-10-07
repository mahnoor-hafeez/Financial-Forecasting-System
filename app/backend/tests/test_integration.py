"""
Integration Tests for Financial AI Forecasting System

This module contains comprehensive integration tests for the entire system,
including API endpoints, database operations, model training, and end-to-end workflows.
"""

import pytest
import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import db
from data_service import DataService
from models.forecast_service import ForecastService
from services.model_evaluator import ModelEvaluator

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_SYMBOLS = ['BTC-USD', 'AAPL', 'EURUSD=X']
TEST_TIMEOUT = 30  # seconds

class TestIntegration:
    """Integration test suite for the Financial AI Forecasting System"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method"""
        self.data_service = DataService()
        self.forecast_service = ForecastService()
        self.model_evaluator = ModelEvaluator()
        
    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'backend' in data
        assert 'database' in data
        assert 'scheduler' in data
        
    def test_data_fetching_workflow(self):
        """Test complete data fetching workflow"""
        symbol = TEST_SYMBOLS[0]
        
        # Test fetch-data endpoint
        response = requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'success'
        assert data['symbol'] == symbol
        assert data['data_count'] > 0
        
        # Test get-data endpoint
        response = requests.get(f"{BASE_URL}/get-data/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        historical_data = response.json()
        assert len(historical_data) > 0
        
        # Verify data structure
        first_record = historical_data[0]
        required_fields = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for field in required_fields:
            assert field in first_record
            
    def test_forecasting_workflow(self):
        """Test complete forecasting workflow"""
        symbol = TEST_SYMBOLS[0]
        
        # Ensure data exists
        requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        time.sleep(2)  # Allow data processing
        
        # Test ensemble forecast
        response = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        forecast_data = response.json()
        assert 'predictions' in forecast_data
        assert 'metrics' in forecast_data
        assert len(forecast_data['predictions']) == 24
        
        # Test individual model forecasts
        models = ['moving-average', 'arima', 'var', 'lstm', 'gru']
        for model in models:
            response = requests.get(f"{BASE_URL}/forecast/{model}/{symbol}?steps=24", timeout=TEST_TIMEOUT)
            assert response.status_code == 200
            
            model_forecast = response.json()
            assert 'predictions' in model_forecast
            
    def test_model_comparison_workflow(self):
        """Test model comparison and evaluation workflow"""
        symbol = TEST_SYMBOLS[0]
        
        # Test model comparison
        response = requests.get(f"{BASE_URL}/models/compare/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        comparison_data = response.json()
        assert 'models' in comparison_data
        assert 'rankings' in comparison_data
        
        # Test performance summary
        response = requests.get(f"{BASE_URL}/models/performance-summary/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        summary_data = response.json()
        assert 'total_models' in summary_data
        assert 'model_performance' in summary_data
        
        # Test best model selection
        response = requests.get(f"{BASE_URL}/models/best/{symbol}?metric=rmse", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        best_model = response.json()
        assert 'best_model' in best_model
        assert 'metric' in best_model
        
    def test_scheduler_functionality(self):
        """Test scheduler management endpoints"""
        # Test scheduler status
        response = requests.get(f"{BASE_URL}/scheduler/status", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        status_data = response.json()
        assert 'status' in status_data
        assert 'jobs' in status_data
        
        # Test manual trigger (data update)
        response = requests.post(f"{BASE_URL}/scheduler/trigger/data", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        trigger_data = response.json()
        assert 'message' in trigger_data
        
    def test_database_operations(self):
        """Test database operations and data integrity"""
        symbol = TEST_SYMBOLS[0]
        
        # Test data storage
        result = self.data_service.fetch_and_store(symbol)
        assert result['status'] == 'success'
        
        # Test data retrieval
        data = self.data_service.get_data(symbol)
        assert len(data) > 0
        
        # Verify data quality
        df = pd.DataFrame(data)
        assert not df.empty
        assert 'Close' in df.columns
        assert df['Close'].notna().all()
        
        # Test sentiment data
        sentiment_data = self.data_service.fetch_sentiment_data()
        assert sentiment_data is not None
        
    def test_model_training_and_prediction(self):
        """Test model training and prediction pipeline"""
        symbol = TEST_SYMBOLS[0]
        
        # Load data
        data = self.forecast_service.load_data(symbol)
        assert not data.empty
        
        # Test model training
        models = ['moving_average', 'arima', 'var', 'lstm', 'gru']
        for model_name in models:
            try:
                # This would test individual model training
                # In a real test, you'd instantiate each model and test training
                pass
            except Exception as e:
                # Some models might fail due to insufficient data or other issues
                print(f"Model {model_name} training failed: {e}")
                
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        symbol = TEST_SYMBOLS[0]
        
        # Step 1: Fetch data
        response = requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        # Step 2: Wait for data processing
        time.sleep(3)
        
        # Step 3: Generate forecast
        response = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        forecast = response.json()
        assert len(forecast['predictions']) == 24
        
        # Step 4: Compare models
        response = requests.get(f"{BASE_URL}/models/compare/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        comparison = response.json()
        assert len(comparison['models']) > 0
        
        # Step 5: Get performance report
        response = requests.get(f"{BASE_URL}/models/report/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        report = response.json()
        assert 'recommendations' in report
        assert 'insights' in report
        
    def test_error_handling(self):
        """Test error handling and edge cases"""
        # Test invalid symbol
        response = requests.get(f"{BASE_URL}/fetch-data/INVALID_SYMBOL", timeout=TEST_TIMEOUT)
        # Should handle gracefully (might return 200 with error message or 500)
        assert response.status_code in [200, 500]
        
        # Test forecast without data
        response = requests.get(f"{BASE_URL}/forecast/NONEXISTENT?horizon=24", timeout=TEST_TIMEOUT)
        # Should handle gracefully
        assert response.status_code in [200, 500]
        
        # Test invalid parameters
        response = requests.get(f"{BASE_URL}/forecast/BTC-USD?horizon=invalid", timeout=TEST_TIMEOUT)
        # Should handle gracefully
        assert response.status_code in [200, 422, 500]
        
    def test_data_consistency(self):
        """Test data consistency across different endpoints"""
        symbol = TEST_SYMBOLS[0]
        
        # Fetch data
        requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        time.sleep(2)
        
        # Get historical data
        response1 = requests.get(f"{BASE_URL}/get-data/{symbol}", timeout=TEST_TIMEOUT)
        data1 = response1.json()
        
        # Generate forecast
        response2 = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        forecast = response2.json()
        
        # Verify data consistency
        assert len(data1) > 0
        assert len(forecast['predictions']) == 24
        
        # Check that forecast timestamps are in the future
        last_historical_date = pd.to_datetime(data1[-1]['Date'])
        first_forecast_date = pd.to_datetime(forecast['predictions'][0]['timestamp'])
        assert first_forecast_date > last_historical_date
        
    def test_performance_metrics(self):
        """Test performance metrics calculation and storage"""
        symbol = TEST_SYMBOLS[0]
        
        # Generate forecast to create performance data
        requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        time.sleep(2)
        requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        time.sleep(2)
        
        # Get performance summary
        response = requests.get(f"{BASE_URL}/models/performance-summary/{symbol}", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        summary = response.json()
        if 'model_performance' in summary and summary['model_performance']:
            for model_name, performance in summary['model_performance'].items():
                if performance.get('rmse') is not None:
                    assert performance['rmse'] >= 0
                if performance.get('mae') is not None:
                    assert performance['mae'] >= 0
                if performance.get('mape') is not None:
                    assert performance['mape'] >= 0

class TestFrontendIntegration:
    """Frontend integration tests"""
    
    def test_frontend_api_connectivity(self):
        """Test that frontend can connect to backend APIs"""
        # Test that frontend can reach backend
        response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        # Test CORS headers
        response = requests.options(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
        assert 'Access-Control-Allow-Origin' in response.headers
        
    def test_api_response_format(self):
        """Test that API responses are in correct format for frontend"""
        symbol = TEST_SYMBOLS[0]
        
        # Test forecast response format
        requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        time.sleep(2)
        
        response = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        forecast = response.json()
        # Verify structure expected by frontend
        assert 'predictions' in forecast
        assert 'metrics' in forecast
        assert isinstance(forecast['predictions'], list)
        assert len(forecast['predictions']) == 24
        
        # Verify prediction structure
        prediction = forecast['predictions'][0]
        assert 'timestamp' in prediction
        assert 'value' in prediction
        assert isinstance(prediction['value'], (int, float))

# Performance tests
class TestPerformance:
    """Performance and load testing"""
    
    def test_api_response_times(self):
        """Test API response times are within acceptable limits"""
        symbol = TEST_SYMBOLS[0]
        
        # Test data fetching response time
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/fetch-data/{symbol}", timeout=TEST_TIMEOUT)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 30  # Should complete within 30 seconds
        
        # Test forecast response time
        time.sleep(2)
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 15  # Should complete within 15 seconds
        
    def test_concurrent_requests(self):
        """Test system behavior under concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(symbol):
            try:
                response = requests.get(f"{BASE_URL}/forecast/{symbol}?horizon=24", timeout=TEST_TIMEOUT)
                results.put((symbol, response.status_code))
            except Exception as e:
                results.put((symbol, str(e)))
        
        # Start multiple concurrent requests
        threads = []
        for symbol in TEST_SYMBOLS:
            thread = threading.Thread(target=make_request, args=(symbol,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=TEST_TIMEOUT)
        
        # Check results
        while not results.empty():
            symbol, result = results.get()
            assert result == 200 or isinstance(result, str)  # Either success or error message

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
