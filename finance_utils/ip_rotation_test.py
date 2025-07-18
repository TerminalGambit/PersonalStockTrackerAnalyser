#!/usr/bin/env python3
"""
IP Rotation Test Script for Yahoo Finance Rate Limits
"""

import requests
import time
import random
from datetime import datetime

def test_yahoo_with_proxies():
    """Test Yahoo Finance with different proxy configurations"""
    
    # Free proxy list (rotate through these)
    free_proxies = [
        # Add some free proxies here - but note they're unreliable
        # Format: {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
    ]
    
    # Test with different user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101',
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("=== Testing Yahoo Finance Access ===")
    print(f"Current time: {datetime.now()}")
    
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL'
    
    # Test without proxy first
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Direct request: {response.status_code}")
        if response.status_code == 200:
            print("✅ Direct access works!")
            return True
    except Exception as e:
        print(f"Direct request failed: {e}")
    
    # Test with proxies (if available)
    for i, proxy in enumerate(free_proxies):
        try:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
            print(f"Proxy {i+1}: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Proxy {i+1} works!")
                return True
        except Exception as e:
            print(f"Proxy {i+1} failed: {e}")
    
    return False

def check_current_ip():
    """Check current public IP"""
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"Current IP: {ip_info['origin']}")
            return ip_info['origin']
    except Exception as e:
        print(f"Failed to get IP: {e}")
    return None

if __name__ == "__main__":
    current_ip = check_current_ip()
    success = test_yahoo_with_proxies()
    
    if not success:
        print("\n❌ All methods failed. Consider:")
        print("1. Using a VPN to change your IP")
        print("2. Waiting 24-48 hours for rate limit reset")
        print("3. Using alternative data sources")
        print("4. Implementing request delays and retries")
