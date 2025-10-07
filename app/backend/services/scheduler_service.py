"""
Automated Data Update Service
Handles scheduled data fetching and model retraining
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_service import DataService
from models.forecast_service import ForecastService
from db_config import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Automated scheduling service for data updates and model retraining
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.data_service = DataService()
        self.forecast_service = ForecastService()
        self.symbols = ['BTC-USD', 'AAPL', 'EURUSD=X', 'TSLA', 'GOOGL']
        
    def start_scheduler(self):
        """Start the background scheduler with all jobs"""
        try:
            # Daily data update at 6:00 AM EST
            self.scheduler.add_job(
                func=self.daily_data_update,
                trigger=CronTrigger(hour=6, minute=0, timezone='US/Eastern'),
                id='daily_data_update',
                name='Daily Market Data Update',
                replace_existing=True
            )
            
            # Hourly forecast refresh during market hours (9 AM - 4 PM EST)
            self.scheduler.add_job(
                func=self.hourly_forecast_refresh,
                trigger=CronTrigger(hour='9-16', minute=0, timezone='US/Eastern'),
                id='hourly_forecast_refresh',
                name='Hourly Forecast Refresh',
                replace_existing=True
            )
            
            # Weekly model retraining on Sundays at 2:00 AM EST
            self.scheduler.add_job(
                func=self.weekly_model_retrain,
                trigger=CronTrigger(day_of_week='sun', hour=2, minute=0, timezone='US/Eastern'),
                id='weekly_model_retrain',
                name='Weekly Model Retraining',
                replace_existing=True
            )
            
            # Sentiment data update every 4 hours
            self.scheduler.add_job(
                func=self.sentiment_update,
                trigger=IntervalTrigger(hours=4),
                id='sentiment_update',
                name='Sentiment Data Update',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("✅ Scheduler started successfully")
            logger.info("📅 Jobs scheduled:")
            logger.info("   - Daily data update: 6:00 AM EST")
            logger.info("   - Hourly forecast refresh: 9 AM - 4 PM EST")
            logger.info("   - Weekly model retraining: Sunday 2:00 AM EST")
            logger.info("   - Sentiment updates: Every 4 hours")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
    
    def daily_data_update(self):
        """Update market data for all symbols daily"""
        logger.info("🔄 Starting daily data update...")
        
        for symbol in self.symbols:
            try:
                logger.info(f"📊 Updating data for {symbol}")
                
                # Fetch fresh market data
                market_data = self.data_service.fetch_market_data(symbol, period='1y')
                if market_data is not None and not market_data.empty:
                    # Store in database
                    self.data_service.store_market_data(symbol, market_data)
                    logger.info(f"✅ {symbol} data updated successfully")
                else:
                    logger.warning(f"⚠️ No data received for {symbol}")
                    
            except Exception as e:
                logger.error(f"❌ Error updating {symbol}: {e}")
                
        logger.info("✅ Daily data update completed")
    
    def hourly_forecast_refresh(self):
        """Refresh forecasts for all symbols hourly during market hours"""
        logger.info("🔄 Starting hourly forecast refresh...")
        
        for symbol in self.symbols:
            try:
                logger.info(f"🔮 Refreshing forecasts for {symbol}")
                
                # Generate fresh forecasts
                forecasts = self.forecast_service.forecast_ensemble(symbol, horizon=24)
                if forecasts:
                    logger.info(f"✅ {symbol} forecasts refreshed")
                else:
                    logger.warning(f"⚠️ No forecasts generated for {symbol}")
                    
            except Exception as e:
                logger.error(f"❌ Error refreshing forecasts for {symbol}: {e}")
                
        logger.info("✅ Hourly forecast refresh completed")
    
    def weekly_model_retrain(self):
        """Retrain all models weekly"""
        logger.info("🔄 Starting weekly model retraining...")
        
        for symbol in self.symbols:
            try:
                logger.info(f"🧠 Retraining models for {symbol}")
                
                # Retrain all models
                self.forecast_service.retrain_models(symbol)
                logger.info(f"✅ {symbol} models retrained")
                
            except Exception as e:
                logger.error(f"❌ Error retraining models for {symbol}: {e}")
                
        logger.info("✅ Weekly model retraining completed")
    
    def sentiment_update(self):
        """Update sentiment data every 4 hours"""
        logger.info("🔄 Starting sentiment update...")
        
        try:
            # Fetch fresh sentiment data
            sentiment_data = self.data_service.fetch_sentiment_data()
            if sentiment_data:
                # Store in database
                self.data_service.store_sentiment_data(sentiment_data)
                logger.info("✅ Sentiment data updated")
            else:
                logger.warning("⚠️ No sentiment data received")
                
        except Exception as e:
            logger.error(f"❌ Error updating sentiment: {e}")
            
        logger.info("✅ Sentiment update completed")
    
    def get_scheduler_status(self):
        """Get current scheduler status and job information"""
        if not self.scheduler.running:
            return {"status": "stopped", "jobs": []}
            
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
            
        return {
            "status": "running",
            "jobs": jobs,
            "total_jobs": len(jobs)
        }
    
    def trigger_manual_update(self, update_type="all"):
        """Manually trigger updates for testing"""
        logger.info(f"🔄 Manual {update_type} update triggered")
        
        if update_type in ["all", "data"]:
            self.daily_data_update()
        if update_type in ["all", "forecast"]:
            self.hourly_forecast_refresh()
        if update_type in ["all", "sentiment"]:
            self.sentiment_update()
        if update_type in ["all", "models"]:
            self.weekly_model_retrain()

# Global scheduler instance
scheduler_service = SchedulerService()
