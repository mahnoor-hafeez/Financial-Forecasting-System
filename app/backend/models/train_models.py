import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Import models
from arima_model import ARIMAForecaster
from moving_average_model import MovingAverageForecaster
from var_model import VARForecaster
from lstm_model import LSTMForecaster
from gru_model import GRUForecaster
from ensemble_model import EnsembleForecaster
from model_evaluator import ModelEvaluator

# Import database connection
from db_config import db

class ModelTrainer:
    def __init__(self, symbol='BTC-USD'):
        self.symbol = symbol
        self.data = None
        self.train_data = None
        self.test_data = None
        self.evaluator = ModelEvaluator()
        self.models = {}
        
    def load_data(self):
        """Load data from MongoDB"""
        try:
            # Load historical data
            cursor = db.historical_data.find({'Symbol': self.symbol}).sort('Date', 1)
            self.data = pd.DataFrame(list(cursor))
            
            if self.data.empty:
                raise ValueError(f"No data found for symbol {self.symbol}")
                
            # Convert Date column
            self.data['Date'] = pd.to_datetime(self.data['Date'])
            self.data.set_index('Date', inplace=True)
            
            # Sort by date
            self.data.sort_index(inplace=True)
            
            print(f"Loaded {len(self.data)} records for {self.symbol}")
            print(f"Date range: {self.data.index.min()} to {self.data.index.max()}")
            
            return self.data
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None
    
    def split_data(self, test_size=0.2):
        """Split data into train and test sets"""
        if self.data is None:
            raise ValueError("Data must be loaded first")
            
        split_idx = int(len(self.data) * (1 - test_size))
        self.train_data = self.data.iloc[:split_idx]
        self.test_data = self.data.iloc[split_idx:]
        
        print(f"Train data: {len(self.train_data)} records")
        print(f"Test data: {len(self.test_data)} records")
        
        return self.train_data, self.test_data
    
    def train_baseline_models(self):
        """Train baseline models (Moving Average, ARIMA, VAR)"""
        print("\n=== Training Baseline Models ===")
        
        # 1. Moving Average Model
        try:
            print("Training Moving Average model...")
            ma_model = MovingAverageForecaster(window_size=20)
            ma_model.train(self.train_data)
            self.models['MovingAverage'] = ma_model
            print("✓ Moving Average model trained")
        except Exception as e:
            print(f"✗ Moving Average model failed: {str(e)}")
        
        # 2. ARIMA Model
        try:
            print("Training ARIMA model...")
            arima_model = ARIMAForecaster()
            arima_model.train(self.train_data)
            self.models['ARIMA'] = arima_model
            print("✓ ARIMA model trained")
        except Exception as e:
            print(f"✗ ARIMA model failed: {str(e)}")
        
        # 3. VAR Model
        try:
            print("Training VAR model...")
            var_model = VARForecaster()
            var_model.train(self.train_data)
            self.models['VAR'] = var_model
            print("✓ VAR model trained")
        except Exception as e:
            print(f"✗ VAR model failed: {str(e)}")
    
    def train_neural_models(self):
        """Train neural models (LSTM, GRU)"""
        print("\n=== Training Neural Models ===")
        
        # Check if we have enough data for neural models
        if len(self.train_data) < 200:
            print("⚠ Insufficient data for neural models. Skipping...")
            return
        
        # 1. LSTM Model
        try:
            print("Training LSTM model...")
            lstm_model = LSTMForecaster(sequence_length=60, epochs=20, batch_size=16)
            lstm_model.train(self.train_data)
            self.models['LSTM'] = lstm_model
            print("✓ LSTM model trained")
        except Exception as e:
            print(f"✗ LSTM model failed: {str(e)}")
        
        # 2. GRU Model
        try:
            print("Training GRU model...")
            gru_model = GRUForecaster(sequence_length=60, epochs=20, batch_size=16)
            gru_model.train(self.train_data)
            self.models['GRU'] = gru_model
            print("✓ GRU model trained")
        except Exception as e:
            print(f"✗ GRU model failed: {str(e)}")
    
    def create_ensemble(self):
        """Create and train ensemble model"""
        print("\n=== Creating Ensemble Model ===")
        
        if len(self.models) < 2:
            print("⚠ Need at least 2 models for ensemble. Skipping...")
            return
        
        try:
            ensemble = EnsembleForecaster()
            
            # Add all trained models to ensemble
            for name, model in self.models.items():
                ensemble.add_model(name, model)
            
            # Set equal weights initially
            ensemble.normalize_weights()
            
            # Optimize weights using validation data
            if len(self.train_data) > 100:
                validation_data = self.train_data.tail(50)
                ensemble.optimize_weights(validation_data)
            
            self.models['Ensemble'] = ensemble
            print("✓ Ensemble model created")
            
        except Exception as e:
            print(f"✗ Ensemble model failed: {str(e)}")
    
    def evaluate_models(self):
        """Evaluate all trained models"""
        print("\n=== Evaluating Models ===")
        
        for name, model in self.models.items():
            try:
                print(f"Evaluating {name}...")
                result = self.evaluator.evaluate_model(
                    model, self.test_data, name, 
                    model.get_model_info() if hasattr(model, 'get_model_info') else {}
                )
                if result:
                    print(f"✓ {name} - RMSE: {result['metrics']['rmse']:.6f}, MAE: {result['metrics']['mae']:.6f}")
                else:
                    print(f"✗ {name} evaluation failed")
            except Exception as e:
                print(f"✗ {name} evaluation failed: {str(e)}")
    
    def save_models(self):
        """Save trained models to files"""
        print("\n=== Saving Models ===")
        
        # Create models directory if it doesn't exist
        models_dir = f"models/{self.symbol}"
        os.makedirs(models_dir, exist_ok=True)
        
        for name, model in self.models.items():
            try:
                if hasattr(model, 'save_model'):
                    filepath = f"{models_dir}/{name.lower()}_model.h5"
                    model.save_model(filepath)
                    print(f"✓ {name} saved to {filepath}")
                else:
                    # For non-neural models, save as pickle
                    import pickle
                    filepath = f"{models_dir}/{name.lower()}_model.pkl"
                    with open(filepath, 'wb') as f:
                        pickle.dump(model, f)
                    print(f"✓ {name} saved to {filepath}")
            except Exception as e:
                print(f"✗ Failed to save {name}: {str(e)}")
    
    def save_results_to_db(self):
        """Save evaluation results to MongoDB"""
        print("\n=== Saving Results to Database ===")
        self.evaluator.save_results_to_db(self.symbol)
    
    def print_summary(self):
        """Print training summary"""
        print("\n" + "="*50)
        print("TRAINING SUMMARY")
        print("="*50)
        
        print(f"Symbol: {self.symbol}")
        print(f"Total data points: {len(self.data)}")
        print(f"Train data: {len(self.train_data)}")
        print(f"Test data: {len(self.test_data)}")
        print(f"Models trained: {len(self.models)}")
        
        # Print model comparison
        comparison = self.evaluator.compare_models()
        if not comparison.empty:
            print("\nModel Performance Comparison:")
            print(comparison.to_string(index=False))
        
        # Print best model
        best_model = self.evaluator.get_best_model('rmse')
        if best_model:
            print(f"\nBest Model: {best_model['model_name']} (RMSE: {best_model['metrics']['rmse']:.6f})")
        
        print("="*50)
    
    def train_all(self):
        """Train all models and evaluate"""
        print(f"Starting model training for {self.symbol}")
        print("="*50)
        
        # Load data
        data = self.load_data()
        if data is None or data.empty:
            return False
        
        # Split data
        self.split_data()
        
        # Train models
        self.train_baseline_models()
        self.train_neural_models()
        self.create_ensemble()
        
        # Evaluate models
        self.evaluate_models()
        
        # Save models and results
        self.save_models()
        self.save_results_to_db()
        
        # Print summary
        self.print_summary()
        
        return True

def main():
    """Main training function"""
    # List of symbols to train
    symbols = ['BTC-USD', 'AAPL', 'EURUSD=X']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"Training models for {symbol}")
        print(f"{'='*60}")
        
        trainer = ModelTrainer(symbol)
        success = trainer.train_all()
        
        if success:
            print(f"✓ Training completed for {symbol}")
        else:
            print(f"✗ Training failed for {symbol}")

if __name__ == "__main__":
    main()
