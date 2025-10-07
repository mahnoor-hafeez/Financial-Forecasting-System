"""
Model Performance Evaluation and Comparison System
Provides comprehensive analysis and comparison of all forecasting models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import database connection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import db

class ModelEvaluator:
    """
    Comprehensive model evaluation and comparison system
    """
    
    def __init__(self):
        self.metrics = ['rmse', 'mae', 'mape']
        self.models = ['moving_average', 'arima', 'var', 'lstm', 'gru', 'ensemble']
        
    def get_all_performance_data(self, symbol: str = None) -> pd.DataFrame:
        """Get all performance data from database"""
        try:
            query = {}
            if symbol:
                query['symbol'] = symbol
                
            cursor = db.model_performance.find(query).sort('timestamp', -1)
            data = pd.DataFrame(list(cursor))
            
            if data.empty:
                return pd.DataFrame()
                
            # Convert timestamp to datetime
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            return data
            
        except Exception as e:
            print(f"Error fetching performance data: {e}")
            return pd.DataFrame()
    
    def calculate_model_rankings(self, symbol: str = None) -> Dict:
        """Calculate model rankings based on performance metrics"""
        data = self.get_all_performance_data(symbol)
        
        if data.empty:
            return {"error": "No performance data available"}
        
        rankings = {}
        
        for metric in self.metrics:
            # Get latest performance for each model
            latest_data = data.groupby('model_name').first().reset_index()
            
            # Extract metrics from the nested structure
            metric_values = []
            for _, row in latest_data.iterrows():
                metrics = row.get('metrics', {})
                metric_values.append(metrics.get(metric, float('inf')))
            
            latest_data[f'{metric}_value'] = metric_values
            
            if f'{metric}_value' in latest_data.columns:
                # Sort by metric (lower is better for RMSE, MAE, MAPE)
                sorted_data = latest_data.sort_values(f'{metric}_value', ascending=True)
                
                rankings[metric] = {
                    'best': sorted_data.iloc[0]['model_name'] if not sorted_data.empty else None,
                    'worst': sorted_data.iloc[-1]['model_name'] if not sorted_data.empty else None,
                    'scores': dict(zip(sorted_data['model_name'], sorted_data[f'{metric}_value']))
                }
        
        return rankings
    
    def get_performance_summary(self, symbol: str = None) -> Dict:
        """Get comprehensive performance summary"""
        data = self.get_all_performance_data(symbol)
        
        if data.empty:
            return {"error": "No performance data available"}
        
        # Get latest performance for each model
        latest_data = data.groupby('model_name').first().reset_index()
        
        summary = {
            'total_models': len(latest_data),
            'symbols_tested': data['symbol'].nunique() if 'symbol' in data.columns else 0,
            'last_update': data['timestamp'].max().isoformat() if not data.empty else None,
            'model_performance': {}
        }
        
        for _, row in latest_data.iterrows():
            model_name = row['model_name']
            summary['model_performance'][model_name] = {
                'rmse': row.get('rmse'),
                'mae': row.get('mae'),
                'mape': row.get('mape'),
                'last_trained': row['timestamp'].isoformat(),
                'model_params': row.get('model_params', {})
            }
        
        return summary
    
    def compare_models(self, symbol: str = None) -> Dict:
        """Compare all models side by side"""
        data = self.get_all_performance_data(symbol)
        
        if data.empty:
            return {"error": "No performance data available"}
        
        # Get latest performance for each model
        latest_data = data.groupby('model_name').first().reset_index()
        
        comparison = {
            'symbol': symbol or 'All Symbols',
            'comparison_date': datetime.now().isoformat(),
            'models': {}
        }
        
        for _, row in latest_data.iterrows():
            model_name = row['model_name']
            metrics = row.get('metrics', {})
            comparison['models'][model_name] = {
                'rmse': metrics.get('rmse'),
                'mae': metrics.get('mae'),
                'mape': metrics.get('mape'),
                'performance_score': self._calculate_performance_score(row),
                'last_trained': row['timestamp'].isoformat(),
                'model_type': self._get_model_type(model_name)
            }
        
        # Add rankings
        comparison['rankings'] = self.calculate_model_rankings(symbol)
        
        return comparison
    
    def _calculate_performance_score(self, row) -> float:
        """Calculate overall performance score (0-100, higher is better)"""
        try:
            metrics = row.get('metrics', {})
            rmse = metrics.get('rmse', float('inf'))
            mae = metrics.get('mae', float('inf'))
            mape = metrics.get('mape', float('inf'))
            
            # Normalize metrics (assuming reasonable ranges)
            rmse_score = max(0, 100 - (rmse / 10) * 100) if rmse != float('inf') else 0
            mae_score = max(0, 100 - (mae / 5) * 100) if mae != float('inf') else 0
            mape_score = max(0, 100 - mape) if mape != float('inf') else 0
            
            # Weighted average
            overall_score = (rmse_score * 0.4 + mae_score * 0.3 + mape_score * 0.3)
            return round(overall_score, 2)
            
        except:
            return 0.0
    
    def _get_model_type(self, model_name: str) -> str:
        """Get model type category"""
        if model_name in ['moving_average', 'arima', 'var']:
            return 'Traditional'
        elif model_name in ['lstm', 'gru']:
            return 'Neural Network'
        elif model_name == 'ensemble':
            return 'Ensemble'
        else:
            return 'Unknown'
    
    def get_best_model(self, symbol: str = None, metric: str = 'rmse') -> Dict:
        """Get the best performing model for a specific metric"""
        rankings = self.calculate_model_rankings(symbol)
        
        if 'error' in rankings:
            return rankings
        
        if metric not in rankings:
            return {"error": f"Metric {metric} not available"}
        
        best_model = rankings[metric]['best']
        best_score = rankings[metric]['scores'].get(best_model)
        
        return {
            'symbol': symbol or 'All Symbols',
            'best_model': best_model,
            'metric': metric,
            'score': best_score,
            'model_type': self._get_model_type(best_model),
            'recommendation': self._get_model_recommendation(best_model, metric)
        }
    
    def _get_model_recommendation(self, model_name: str, metric: str) -> str:
        """Get recommendation for model usage"""
        recommendations = {
            'moving_average': 'Good for short-term trends, simple and fast',
            'arima': 'Excellent for time series with clear patterns',
            'var': 'Best for multivariate analysis with multiple indicators',
            'lstm': 'Superior for complex patterns and long sequences',
            'gru': 'Efficient neural network, good balance of performance and speed',
            'ensemble': 'Most robust, combines strengths of all models'
        }
        
        return recommendations.get(model_name, 'Model performance varies by market conditions')
    
    def generate_performance_report(self, symbol: str = None) -> Dict:
        """Generate comprehensive performance report"""
        comparison = self.compare_models(symbol)
        summary = self.get_performance_summary(symbol)
        
        if 'error' in comparison:
            return comparison
        
        report = {
            'report_date': datetime.now().isoformat(),
            'symbol': symbol or 'All Symbols',
            'summary': summary,
            'comparison': comparison,
            'recommendations': self._generate_recommendations(comparison),
            'insights': self._generate_insights(comparison)
        }
        
        return report
    
    def _generate_recommendations(self, comparison: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if 'models' in comparison:
            models = comparison['models']
            
            # Find best performing models
            best_rmse = min(models.items(), key=lambda x: x[1].get('rmse', float('inf')))
            best_mae = min(models.items(), key=lambda x: x[1].get('mae', float('inf')))
            best_mape = min(models.items(), key=lambda x: x[1].get('mape', float('inf')))
            
            recommendations.extend([
                f"Best RMSE: {best_rmse[0]} ({best_rmse[1].get('rmse', 'N/A')})",
                f"Best MAE: {best_mae[0]} ({best_mae[1].get('mae', 'N/A')})",
                f"Best MAPE: {best_mape[0]} ({best_mape[1].get('mape', 'N/A')})"
            ])
            
            # Model type analysis
            traditional_models = [name for name, data in models.items() 
                                if data.get('model_type') == 'Traditional']
            neural_models = [name for name, data in models.items() 
                           if data.get('model_type') == 'Neural Network']
            
            if traditional_models and neural_models:
                recommendations.append("Consider ensemble approach combining traditional and neural models")
            
            if len(neural_models) > 1:
                recommendations.append("Multiple neural networks available - consider model selection based on data characteristics")
        
        return recommendations
    
    def _generate_insights(self, comparison: Dict) -> List[str]:
        """Generate insights from performance data"""
        insights = []
        
        if 'models' in comparison:
            models = comparison['models']
            
            # Performance distribution analysis
            rmse_values = [data.get('rmse') for data in models.values() if data.get('rmse')]
            mae_values = [data.get('mae') for data in models.values() if data.get('mae')]
            
            if rmse_values:
                rmse_std = np.std(rmse_values)
                if rmse_std < 0.1:
                    insights.append("Models show consistent performance (low RMSE variance)")
                elif rmse_std > 1.0:
                    insights.append("High performance variance - consider model selection criteria")
            
            # Model type performance
            traditional_performance = [data.get('performance_score', 0) 
                                     for name, data in models.items() 
                                     if data.get('model_type') == 'Traditional']
            neural_performance = [data.get('performance_score', 0) 
                                for name, data in models.items() 
                                if data.get('model_type') == 'Neural Network']
            
            if traditional_performance and neural_performance:
                avg_traditional = np.mean(traditional_performance)
                avg_neural = np.mean(neural_performance)
                
                if avg_neural > avg_traditional + 10:
                    insights.append("Neural networks significantly outperform traditional models")
                elif avg_traditional > avg_neural + 10:
                    insights.append("Traditional models show superior performance")
                else:
                    insights.append("Traditional and neural models show comparable performance")
        
        return insights

# Global evaluator instance
model_evaluator = ModelEvaluator()
