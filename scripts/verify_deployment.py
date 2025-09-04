#!/usr/bin/env python3
"""
Deployment verification script for LBM Arena
Run this after deployment to verify everything is working
"""

import requests
import sys
import json

def test_endpoint(base_url, endpoint, description):
    """Test a single endpoint"""
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        success = response.status_code == 200
        print(f"{'✅' if success else '❌'} {description}: {'PASS' if success else 'FAIL'}")
        if not success:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        return success
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: FAIL (Connection Error)")
        print(f"   Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_deployment.py <backend_url>")
        print("Example: python verify_deployment.py https://lbm-arena-backend.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🔍 Verifying LBM Arena deployment at: {base_url}")
    print("=" * 60)
    
    # Test endpoints
    tests = [
        ("/health", "Health Check"),
        ("/", "Root Endpoint"),
        ("/api/v1/players/", "Players API"),
        ("/api/v1/games/", "Games API"),
        ("/api/v1/chess/", "Chess API"),
    ]
    
    results = []
    for endpoint, description in tests:
        results.append(test_endpoint(base_url, endpoint, description))
    
    print("=" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✅ Your LBM Arena deployment is working correctly!")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("❌ Please check the deployment logs and configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
