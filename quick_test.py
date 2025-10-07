#!/usr/bin/env python3
"""
Quick Test Script for Financial AI Forecasting System

This script tests all the major components of the system to ensure everything is working correctly.
Run this after starting both backend and frontend servers.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:3000"
TEST_SYMBOL = "BTC-USD"

def test_backend_health():
    """Test backend health check"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data['status']}")
            print(f"✅ Database: {data['database']}")
            print(f"✅ Scheduler: {data['scheduler']['status']}")
            return True
        else:
            print(f"❌ Backend Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health Check Error: {e}")
        return False

def test_data_fetching():
    """Test data fetching functionality"""
    print("\n📊 Testing Data Fetching...")
    try:
        # Fetch data
        response = requests.get(f"{BACKEND_URL}/fetch-data/{TEST_SYMBOL}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data Fetch: {data['status']}")
            print(f"✅ Records Stored: {data['data_count']}")
            
            # Get data
            response = requests.get(f"{BACKEND_URL}/get-data/{TEST_SYMBOL}", timeout=10)
            if response.status_code == 200:
                historical_data = response.json()
                print(f"✅ Data Retrieval: {len(historical_data)} records")
                return True
            else:
                print(f"❌ Data Retrieval Failed: {response.status_code}")
                return False
        else:
            print(f"❌ Data Fetch Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data Fetching Error: {e}")
        return False

def test_forecasting():
    """Test forecasting functionality"""
    print("\n🔮 Testing Forecasting...")
    try:
        # Wait a bit for data processing
        time.sleep(3)
        
        # Test ensemble forecast
        response = requests.get(f"{BACKEND_URL}/forecast/{TEST_SYMBOL}?horizon=24", timeout=30)
        if response.status_code == 200:
            forecast = response.json()
            print(f"✅ Ensemble Forecast: {len(forecast['predictions'])} predictions")
            print(f"✅ Model Used: {forecast['model_used']}")
            print(f"✅ RMSE: {forecast['metrics']['rmse']:.2f}")
            return True
        else:
            print(f"❌ Forecasting Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forecasting Error: {e}")
        return False

def test_model_comparison():
    """Test model comparison functionality"""
    print("\n🧠 Testing Model Comparison...")
    try:
        # Test model comparison
        response = requests.get(f"{BACKEND_URL}/models/compare/{TEST_SYMBOL}", timeout=15)
        if response.status_code == 200:
            comparison = response.json()
            print(f"✅ Model Comparison: {len(comparison['models'])} models compared")
            
            # Test performance summary
            response = requests.get(f"{BACKEND_URL}/models/performance-summary/{TEST_SYMBOL}", timeout=10)
            if response.status_code == 200:
                summary = response.json()
                print(f"✅ Performance Summary: {summary['total_models']} models")
                return True
            else:
                print(f"❌ Performance Summary Failed: {response.status_code}")
                return False
        else:
            print(f"❌ Model Comparison Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model Comparison Error: {e}")
        return False

def test_scheduler():
    """Test scheduler functionality"""
    print("\n⏰ Testing Scheduler...")
    try:
        # Test scheduler status
        response = requests.get(f"{BACKEND_URL}/scheduler/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Scheduler Status: {status['status']}")
            print(f"✅ Total Jobs: {status['total_jobs']}")
            
            # Test manual trigger
            response = requests.post(f"{BACKEND_URL}/scheduler/trigger/sentiment", timeout=10)
            if response.status_code == 200:
                print("✅ Manual Trigger: Success")
                return True
            else:
                print(f"❌ Manual Trigger Failed: {response.status_code}")
                return False
        else:
            print(f"❌ Scheduler Status Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Scheduler Error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("\n🎨 Testing Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Accessible")
            return True
        else:
            print(f"❌ Frontend Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔗 Testing API Endpoints...")
    
    endpoints = [
        ("Health Check", f"{BACKEND_URL}/health"),
        ("Fetch Data", f"{BACKEND_URL}/fetch-data/{TEST_SYMBOL}"),
        ("Get Data", f"{BACKEND_URL}/get-data/{TEST_SYMBOL}"),
        ("Forecast", f"{BACKEND_URL}/forecast/{TEST_SYMBOL}?horizon=24"),
        ("Model Compare", f"{BACKEND_URL}/models/compare/{TEST_SYMBOL}"),
        ("Performance Summary", f"{BACKEND_URL}/models/performance-summary/{TEST_SYMBOL}"),
        ("Scheduler Status", f"{BACKEND_URL}/scheduler/status"),
    ]
    
    results = []
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                results.append(True)
            else:
                print(f"❌ {name}: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Main test function"""
    print("🧪 Financial AI Forecasting System - Quick Test")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Test Symbol: {TEST_SYMBOL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Backend Health", test_backend_health),
        ("Data Fetching", test_data_fetching),
        ("Forecasting", test_forecasting),
        ("Model Comparison", test_model_comparison),
        ("Scheduler", test_scheduler),
        ("Frontend", test_frontend),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
        print("\n🌐 Access the application:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend API: {BACKEND_URL}")
        print(f"   API Docs: {BACKEND_URL}/docs")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
