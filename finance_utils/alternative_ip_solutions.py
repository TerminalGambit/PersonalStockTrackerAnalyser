#!/usr/bin/env python3
"""
Alternative IP Solutions for Yahoo Finance Rate Limiting
"""

import requests
import time
import json
import subprocess
from datetime import datetime

class AlternativeIPSolutions:
    def __init__(self):
        self.original_ip = self.get_current_ip()
        print(f"🔍 Current IP: {self.original_ip}")
    
    def get_current_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                return response.json()['origin']
            return "Unable to determine"
        except:
            return "Error"
    
    def test_mobile_hotspot_connectivity(self):
        """Test mobile hotspot connectivity"""
        print("📱 Mobile Hotspot Setup Guide:")
        print("=" * 40)
        print("1. On your iPhone/Android:")
        print("   - Go to Settings > Personal Hotspot (iPhone)")
        print("   - Or Settings > Mobile Hotspot (Android)")
        print("   - Turn on Personal Hotspot/Mobile Hotspot")
        print("   - Note the network name and password")
        print()
        print("2. On your Mac:")
        print("   - Click Wi-Fi icon in menu bar")
        print("   - Select your phone's hotspot network")
        print("   - Enter the password")
        print()
        print("3. Verify connection:")
        
        input("Press Enter when you've connected to mobile hotspot...")
        
        new_ip = self.get_current_ip()
        if new_ip != self.original_ip:
            print(f"✅ Success! New IP: {new_ip}")
            return True
        else:
            print(f"❌ Same IP: {new_ip}")
            return False
    
    def test_yahoo_finance_access(self):
        """Test Yahoo Finance access"""
        print("\n🧪 Testing Yahoo Finance access...")
        current_ip = self.get_current_ip()
        print(f"Current IP: {current_ip}")
        
        try:
            response = requests.get(
                'https://query1.finance.yahoo.com/v8/finance/chart/AAPL',
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Yahoo Finance access successful!")
                return True
            elif response.status_code == 429:
                print("❌ Still rate limited (429)")
                return False
            else:
                print(f"❌ Other error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def get_free_vpn_recommendations(self):
        """Provide free VPN recommendations"""
        print("\n🔒 Free VPN Recommendations:")
        print("=" * 40)
        
        vpns = [
            {
                "name": "Proton VPN",
                "free_tier": "Yes",
                "setup": "Download from protonvpn.com, create account, install app",
                "pros": "No data limits, good privacy",
                "cons": "Limited server locations"
            },
            {
                "name": "Windscribe",
                "free_tier": "10GB/month",
                "setup": "Download from windscribe.com, create account",
                "pros": "Easy to use, multiple locations",
                "cons": "Data limit"
            },
            {
                "name": "TunnelBear",
                "free_tier": "500MB/month",
                "setup": "Download from tunnelbear.com, create account",
                "pros": "Very user-friendly",
                "cons": "Very limited data"
            },
            {
                "name": "Opera Browser Built-in VPN",
                "free_tier": "Unlimited",
                "setup": "Download Opera browser, enable VPN in settings",
                "pros": "Built-in, no separate app needed",
                "cons": "Only works within Opera browser"
            }
        ]
        
        for vpn in vpns:
            print(f"\n📦 {vpn['name']}")
            print(f"   Free Tier: {vpn['free_tier']}")
            print(f"   Setup: {vpn['setup']}")
            print(f"   Pros: {vpn['pros']}")
            print(f"   Cons: {vpn['cons']}")
    
    def get_proxy_solutions(self):
        """Provide proxy solutions"""
        print("\n🌐 Proxy Solutions:")
        print("=" * 40)
        
        print("1. Browser-based proxy testing:")
        print("   - Use online proxy websites")
        print("   - Test Yahoo Finance access through web proxy")
        print("   - Examples: proxysite.com, hide.me")
        print()
        
        print("2. System-wide proxy (requires proxy server):")
        print("   - System Preferences > Network > Advanced > Proxies")
        print("   - Configure HTTP/HTTPS proxy settings")
        print()
        
        print("3. SSH Tunnel (if you have access to remote server):")
        print("   - ssh -D 8080 user@remote-server")
        print("   - Configure SOCKS proxy localhost:8080")
    
    def test_tor_solution(self):
        """Test Tor browser solution"""
        print("\n🧅 Tor Browser Solution:")
        print("=" * 40)
        print("1. Download Tor Browser from torproject.org")
        print("2. Install and launch Tor Browser")
        print("3. Wait for connection to Tor network")
        print("4. Navigate to Yahoo Finance in Tor Browser")
        print("5. Test if rate limiting is bypassed")
        print()
        print("Note: Tor provides anonymity but may be slower")
    
    def get_alternative_data_sources(self):
        """Provide alternative data sources"""
        print("\n📊 Alternative Data Sources:")
        print("=" * 40)
        
        sources = [
            {
                "name": "Alpha Vantage",
                "free_tier": "500 requests/day",
                "setup": "Get free API key from alphavantage.co",
                "python_lib": "pip install alpha-vantage"
            },
            {
                "name": "IEX Cloud",
                "free_tier": "500,000 requests/month",
                "setup": "Get free API key from iexcloud.io",
                "python_lib": "pip install iexfinance"
            },
            {
                "name": "Quandl",
                "free_tier": "Limited datasets",
                "setup": "Get free API key from quandl.com",
                "python_lib": "pip install quandl"
            },
            {
                "name": "Polygon.io",
                "free_tier": "5 requests/minute",
                "setup": "Get free API key from polygon.io",
                "python_lib": "pip install polygon-api-client"
            }
        ]
        
        for source in sources:
            print(f"\n📈 {source['name']}")
            print(f"   Free Tier: {source['free_tier']}")
            print(f"   Setup: {source['setup']}")
            print(f"   Python: {source['python_lib']}")
    
    def run_comprehensive_test(self):
        """Run comprehensive IP change test"""
        print("🚀 Comprehensive IP Change & Access Test")
        print("=" * 50)
        
        print(f"📅 Start time: {datetime.now()}")
        print(f"🔍 Original IP: {self.original_ip}")
        
        # Test current access
        print("\n1. Testing current Yahoo Finance access...")
        current_access = self.test_yahoo_finance_access()
        
        if current_access:
            print("✅ You already have access! No IP change needed.")
            return True
        
        # Try mobile hotspot
        print("\n2. Trying mobile hotspot...")
        print("⚠️  Note: This will use your mobile data!")
        proceed = input("Proceed with mobile hotspot test? (y/N): ")
        
        if proceed.lower() == 'y':
            if self.test_mobile_hotspot_connectivity():
                print("🎉 Mobile hotspot connected successfully!")
                
                if self.test_yahoo_finance_access():
                    print("🎉 Yahoo Finance access restored with mobile hotspot!")
                    return True
                else:
                    print("❌ Still rate limited even with mobile hotspot")
        
        # Provide alternatives
        print("\n3. Alternative solutions:")
        self.get_free_vpn_recommendations()
        self.get_proxy_solutions()
        self.test_tor_solution()
        self.get_alternative_data_sources()
        
        return False

def main():
    """Main function"""
    print("🔧 Alternative IP Solutions for Yahoo Finance")
    print("=" * 50)
    
    solver = AlternativeIPSolutions()
    
    print("\nOptions:")
    print("1. Run comprehensive test (recommended)")
    print("2. Test mobile hotspot only")
    print("3. Get VPN recommendations")
    print("4. Get proxy solutions")
    print("5. Get alternative data sources")
    print("6. Test current Yahoo Finance access")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        solver.run_comprehensive_test()
    elif choice == '2':
        solver.test_mobile_hotspot_connectivity()
        solver.test_yahoo_finance_access()
    elif choice == '3':
        solver.get_free_vpn_recommendations()
    elif choice == '4':
        solver.get_proxy_solutions()
    elif choice == '5':
        solver.get_alternative_data_sources()
    elif choice == '6':
        solver.test_yahoo_finance_access()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
