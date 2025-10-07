#!/usr/bin/env python3
"""
Test Runner for Financial AI Forecasting System

This script runs comprehensive tests including unit tests, integration tests,
and end-to-end tests for the entire system.

Usage:
    python run_tests.py [--unit] [--integration] [--e2e] [--all]
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_backend_running():
    """Check if the backend is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "app" / "backend"
    
    # Start backend in background
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--port", "8001", "--reload"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_running():
            print("✅ Backend server started successfully")
            return process
        time.sleep(1)
    
    print("❌ Failed to start backend server")
    process.terminate()
    return None

def stop_backend(process):
    """Stop the backend server"""
    if process:
        print("🛑 Stopping backend server...")
        process.terminate()
        process.wait()

def run_unit_tests():
    """Run unit tests"""
    print("\n📋 Running Unit Tests...")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent / "app" / "backend"
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_models.py -v",
        cwd=backend_dir
    )
    
    if success:
        print("✅ Unit tests passed")
        print(stdout)
    else:
        print("❌ Unit tests failed")
        print(stderr)
    
    return success

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent / "app" / "backend"
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_integration.py -v",
        cwd=backend_dir
    )
    
    if success:
        print("✅ Integration tests passed")
        print(stdout)
    else:
        print("❌ Integration tests failed")
        print(stderr)
    
    return success

def run_e2e_tests():
    """Run end-to-end tests"""
    print("\n🌐 Running End-to-End Tests...")
    print("=" * 50)
    
    # Test API endpoints
    test_cases = [
        ("Health Check", "curl -s http://127.0.0.1:8001/health"),
        ("Fetch Data", "curl -s http://127.0.0.1:8001/fetch-data/BTC-USD"),
        ("Get Data", "curl -s http://127.0.0.1:8001/get-data/BTC-USD"),
        ("Generate Forecast", "curl -s 'http://127.0.0.1:8001/forecast/BTC-USD?horizon=24'"),
        ("Model Comparison", "curl -s http://127.0.0.1:8001/models/compare/BTC-USD"),
        ("Scheduler Status", "curl -s http://127.0.0.1:8001/scheduler/status")
    ]
    
    all_passed = True
    
    for test_name, command in test_cases:
        print(f"\n🧪 Testing: {test_name}")
        success, stdout, stderr = run_command(command)
        
        if success and stdout.strip():
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
            if stderr:
                print(f"Error: {stderr}")
            all_passed = False
    
    return all_passed

def run_frontend_tests():
    """Run frontend tests (if available)"""
    print("\n🎨 Running Frontend Tests...")
    print("=" * 50)
    
    frontend_dir = Path(__file__).parent / "app" / "frontend"
    
    # Check if frontend tests exist
    if not (frontend_dir / "src" / "__tests__").exists():
        print("⚠️ No frontend tests found, skipping...")
        return True
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
        if not success:
            print(f"❌ Failed to install dependencies: {stderr}")
            return False
    
    # Run tests
    success, stdout, stderr = run_command("npm test -- --coverage --watchAll=false", cwd=frontend_dir)
    
    if success:
        print("✅ Frontend tests passed")
        print(stdout)
    else:
        print("❌ Frontend tests failed")
        print(stderr)
    
    return success

def run_performance_tests():
    """Run performance tests"""
    print("\n⚡ Running Performance Tests...")
    print("=" * 50)
    
    try:
        import requests
        import time
        
        # Test response times
        endpoints = [
            ("/health", 1),
            ("/fetch-data/BTC-USD", 30),
            ("/forecast/BTC-USD?horizon=24", 15),
            ("/models/compare/BTC-USD", 5)
        ]
        
        all_passed = True
        
        for endpoint, max_time in endpoints:
            print(f"\n⏱️ Testing: {endpoint}")
            start_time = time.time()
            
            try:
                response = requests.get(f"http://127.0.0.1:8001{endpoint}", timeout=max_time)
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200 and response_time <= max_time:
                    print(f"✅ {endpoint} - {response_time:.2f}s (PASSED)")
                else:
                    print(f"❌ {endpoint} - {response_time:.2f}s (FAILED)")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {endpoint} - ERROR: {e}")
                all_passed = False
        
        return all_passed
        
    except ImportError:
        print("⚠️ requests library not available, skipping performance tests")
        return True

def generate_test_report(results):
    """Generate a test report"""
    print("\n📊 Test Report")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    return passed_tests == total_tests

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run tests for Financial AI Forecasting System")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # If no specific tests are specified, run all
    if not any([args.unit, args.integration, args.e2e, args.frontend, args.performance]):
        args.all = True
    
    print("🧪 Financial AI Forecasting System - Test Suite")
    print("=" * 60)
    
    # Start backend if needed
    backend_process = None
    if not check_backend_running():
        backend_process = start_backend()
        if not backend_process:
            print("❌ Cannot run tests without backend server")
            return 1
    
    try:
        results = {}
        
        # Run selected tests
        if args.all or args.unit:
            results["Unit Tests"] = run_unit_tests()
        
        if args.all or args.integration:
            results["Integration Tests"] = run_integration_tests()
        
        if args.all or args.e2e:
            results["End-to-End Tests"] = run_e2e_tests()
        
        if args.all or args.frontend:
            results["Frontend Tests"] = run_frontend_tests()
        
        if args.all or args.performance:
            results["Performance Tests"] = run_performance_tests()
        
        # Generate report
        all_passed = generate_test_report(results)
        
        return 0 if all_passed else 1
        
    finally:
        # Clean up
        stop_backend(backend_process)

if __name__ == "__main__":
    sys.exit(main())
