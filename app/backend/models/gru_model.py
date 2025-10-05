import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class GRUForecaster:
    def __init__(self, sequence_length=60, units=50, dropout=0.2, epochs=50, batch_size=32):
        self.sequence_length = sequence_length
        self.units = units
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_columns = ['Close', 'Volume', 'Daily_Return', 'Volatility', 'SMA_7', 'SMA_14', 'EMA_7', 'EMA_14']
        
        self.params = {
            'sequence_length': sequence_length,
            'units': units,
            'dropout': dropout,
            'epochs': epochs,
            'batch_size': batch_size
        }
        
    def prepare_data(self, data):
        """Prepare data for GRU model"""
        # Select relevant columns
        features = data[self.feature_columns].copy()
        
        # Handle missing values
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        # Normalize features
        scaled_features = self.scaler.fit_transform(features)
        
        return scaled_features
    
    def create_sequences(self, data, target_col_idx=0):
        """Create sequences for GRU training"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i, target_col_idx])  # Close price is first column
            
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build GRU model"""
        model = Sequential([
            GRU(self.units, return_sequences=True, input_shape=input_shape),
            Dropout(self.dropout),
            GRU(self.units, return_sequences=False),
            Dropout(self.dropout),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, data, target_column='Close', validation_split=0.2):
        """Train GRU model"""
        # Prepare data
        scaled_data = self.prepare_data(data)
        
        # Create sequences
        X, y = self.create_sequences(scaled_data)
        
        if len(X) < 100:  # Need sufficient data
            raise ValueError("Insufficient data for GRU model. Need at least 100 sequences.")
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Build and train model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self.build_model(input_shape)
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        self.params['training_history'] = history.history
        
        return self
    
    def predict(self, data, steps=24):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model must be trained first")
            
        # Prepare data
        scaled_data = self.prepare_data(data)
        
        # Ensure we have enough data for sequence length
        if len(scaled_data) < self.sequence_length:
            raise ValueError(f"Insufficient data for sequence length {self.sequence_length}")
        
        # Get last sequence with proper feature dimension
        last_sequence_data = scaled_data[-self.sequence_length:]
        
        # Ensure correct shape for reshaping
        if last_sequence_data.ndim == 1:
            # If 1D, reshape to 2D with 1 feature
            last_sequence_data = last_sequence_data.reshape(-1, 1)
        
        # Reshape for GRU input: (batch_size, sequence_length, features)
        last_sequence = last_sequence_data.reshape(1, self.sequence_length, last_sequence_data.shape[1])
        
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            # Predict next value
            next_pred = self.model.predict(current_sequence, verbose=0)
            predictions.append(next_pred[0, 0])
            
            # Update sequence (shift and add prediction)
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = next_pred[0, 0]  # Update Close price
            
        # Inverse transform predictions (only Close price)
        predictions = np.array(predictions).reshape(-1, 1)
        # Create dummy array for inverse transform
        dummy_array = np.zeros((len(predictions), len(self.feature_columns)))
        dummy_array[:, 0] = predictions.flatten()
        predictions = self.scaler.inverse_transform(dummy_array)[:, 0]
        
        return predictions
    
    def evaluate(self, test_data, target_column='Close'):
        """Evaluate model performance"""
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
    
    def save_model(self, filepath):
        """Save model to file"""
        if self.model is None:
            raise ValueError("Model must be trained first")
        self.model.save(filepath)
    
    def load_model(self, filepath):
        """Load model from file"""
        # Handle Keras metrics deserialization issue
        import tensorflow as tf
        try:
            self.model = tf.keras.models.load_model(filepath)
        except Exception as e:
            # Try loading with custom objects for metrics
            try:
                self.model = tf.keras.models.load_model(
                    filepath, 
                    custom_objects={'mse': tf.keras.metrics.mean_squared_error}
                )
            except:
                # If still fails, try without metrics
                self.model = tf.keras.models.load_model(
                    filepath, 
                    compile=False
                )
                # Recompile with simple optimizer
                self.model.compile(
                    optimizer='adam',
                    loss='mse'
                )
    
    def get_model_info(self):
        """Get model parameters"""
        return {
            'model_type': 'GRU',
            'params': self.params,
            'feature_columns': self.feature_columns
        }
