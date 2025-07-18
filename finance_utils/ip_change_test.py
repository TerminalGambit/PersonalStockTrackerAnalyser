#!/usr/bin/env python3
"""
IP Change Testing Script for macOS
This script tests various methods to change your public IP address
"""

import subprocess
import requests
import time
import json
from datetime import datetime

class IPChanger:
    def __init__(self):
        self.original_ip = self.get_current_ip()
        print(f"🔍 Original IP: {self.original_ip}")
    
    def get_current_ip(self):
        """Get current public IP address"""
        try:
            services = [
                'https://httpbin.org/ip',
                'https://api.ipify.org?format=json',
                'https://ifconfig.me/ip',
                'https://icanhazip.com',
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        if 'json' in response.headers.get('content-type', ''):
                            data = response.json()
                            return data.get('origin', data.get('ip'))
                        else:
                            return response.text.strip()
                except:
                    continue
            
            return "Unable to determine"
        except Exception as e:
            print(f"Error getting IP: {e}")
            return "Error"
    
    def get_network_info(self):
        """Get current network interface information"""
        try:
            # Get network interfaces
            result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                  capture_output=True, text=True)
            print("📡 Network Interfaces:")
            print(result.stdout)
            
            # Get current network service
            result = subprocess.run(['networksetup', '-listnetworkserviceorder'], 
                                  capture_output=True, text=True)
            print("\n🔗 Network Service Order:")
            print(result.stdout)
            
            return True
        except Exception as e:
            print(f"Error getting network info: {e}")
            return False
    
    def method_1_restart_network_interface(self):
        """Method 1: Restart network interface to potentially get new DHCP lease"""
        try:
            print("\n🔄 Method 1: Restarting network interface...")
            
            # Get the primary network service (usually Wi-Fi)
            result = subprocess.run(['route', 'get', 'default'], 
                                  capture_output=True, text=True)
            
            # Try to restart Wi-Fi
            print("📡 Turning Wi-Fi off...")
            subprocess.run(['networksetup', '-setairportpower', 'en0', 'off'], 
                          capture_output=True, text=True)
            
            time.sleep(3)
            
            print("📡 Turning Wi-Fi on...")
            subprocess.run(['networksetup', '-setairportpower', 'en0', 'on'], 
                          capture_output=True, text=True)
            
            # Wait for connection
            print("⏳ Waiting for connection...")
            time.sleep(10)
            
            new_ip = self.get_current_ip()
            if new_ip != self.original_ip:
                print(f"✅ Success! New IP: {new_ip}")
                return True
            else:
                print(f"❌ Same IP: {new_ip}")
                return False
                
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            return False
    
    def method_2_renew_dhcp_lease(self):
        """Method 2: Renew DHCP lease"""
        try:
            print("\n🔄 Method 2: Renewing DHCP lease...")
            
            # Try to renew DHCP lease
            result = subprocess.run(['sudo', 'ipconfig', 'set', 'en0', 'DHCP'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ DHCP lease renewal requested")
                time.sleep(5)
                
                new_ip = self.get_current_ip()
                if new_ip != self.original_ip:
                    print(f"✅ Success! New IP: {new_ip}")
                    return True
                else:
                    print(f"❌ Same IP: {new_ip}")
                    return False
            else:
                print(f"❌ DHCP renewal failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            return False
    
    def method_3_flush_dns_and_network(self):
        """Method 3: Flush DNS and network caches"""
        try:
            print("\n🔄 Method 3: Flushing DNS and network caches...")
            
            # Flush DNS cache
            subprocess.run(['sudo', 'dscacheutil', '-flushcache'], 
                          capture_output=True, text=True)
            
            # Flush mDNS cache
            subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], 
                          capture_output=True, text=True)
            
            print("✅ DNS caches flushed")
            time.sleep(2)
            
            new_ip = self.get_current_ip()
            if new_ip != self.original_ip:
                print(f"✅ Success! New IP: {new_ip}")
                return True
            else:
                print(f"❌ Same IP: {new_ip}")
                return False
                
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            return False
    
    def method_4_router_reconnect(self):
        """Method 4: Instructions for router reconnection"""
        print("\n🔄 Method 4: Manual router reconnection")
        print("📋 Manual steps to try:")
        print("1. Unplug your router/modem for 30 seconds")
        print("2. Plug back in and wait 2-3 minutes")
        print("3. This may assign you a new IP from your ISP")
        print("4. Check if your IP changed after reconnection")
        
        input("Press Enter when you've completed the router restart...")
        
        new_ip = self.get_current_ip()
        if new_ip != self.original_ip:
            print(f"✅ Success! New IP: {new_ip}")
            return True
        else:
            print(f"❌ Same IP: {new_ip}")
            return False
    
    def method_5_mobile_hotspot(self):
        """Method 5: Switch to mobile hotspot"""
        print("\n🔄 Method 5: Mobile hotspot switching")
        print("📱 Instructions:")
        print("1. Enable mobile hotspot on your phone")
        print("2. Connect your Mac to the mobile hotspot")
        print("3. This will give you a different IP address")
        print("4. Remember: this uses your mobile data!")
        
        input("Press Enter when you've connected to mobile hotspot...")
        
        new_ip = self.get_current_ip()
        if new_ip != self.original_ip:
            print(f"✅ Success! New IP: {new_ip}")
            return True
        else:
            print(f"❌ Same IP: {new_ip}")
            return False
    
    def test_yahoo_finance_access(self):
        """Test Yahoo Finance access with current IP"""
        print(f"\n🧪 Testing Yahoo Finance access...")
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
    
    def run_all_methods(self):
        """Run all IP change methods sequentially"""
        print("🚀 Starting IP change attempts...")
        print(f"📅 Start time: {datetime.now()}")
        
        # Get network info first
        self.get_network_info()
        
        methods = [
            ("DNS/Cache Flush", self.method_3_flush_dns_and_network),
            ("DHCP Lease Renewal", self.method_2_renew_dhcp_lease),
            ("Network Interface Restart", self.method_1_restart_network_interface),
            ("Router Reconnect", self.method_4_router_reconnect),
            ("Mobile Hotspot", self.method_5_mobile_hotspot),
        ]
        
        for method_name, method_func in methods:
            print(f"\n{'='*50}")
            print(f"🔧 Trying: {method_name}")
            
            try:
                success = method_func()
                if success:
                    print(f"🎉 {method_name} worked!")
                    
                    # Test Yahoo Finance access
                    if self.test_yahoo_finance_access():
                        print("🎉 Yahoo Finance access restored!")
                        return True
                    else:
                        print("⚠️ IP changed but Yahoo Finance still blocked")
                        continue
                else:
                    print(f"❌ {method_name} didn't change IP")
                    
            except Exception as e:
                print(f"❌ {method_name} failed with error: {e}")
            
            # Ask if user wants to continue
            if input("Continue to next method? (y/N): ").lower() != 'y':
                break
        
        print("\n📊 Final Results:")
        final_ip = self.get_current_ip()
        print(f"Original IP: {self.original_ip}")
        print(f"Final IP: {final_ip}")
        
        if final_ip != self.original_ip:
            print("✅ IP address changed successfully!")
            return self.test_yahoo_finance_access()
        else:
            print("❌ IP address remains the same")
            return False

def main():
    """Main function to run IP change tests"""
    print("🔧 macOS IP Address Change Testing Tool")
    print("=" * 50)
    
    changer = IPChanger()
    
    print("\nOptions:")
    print("1. Test all methods automatically")
    print("2. Run specific method")
    print("3. Just test current Yahoo Finance access")
    print("4. Get network information only")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        changer.run_all_methods()
    elif choice == '2':
        print("\nAvailable methods:")
        print("1. DNS/Cache Flush")
        print("2. DHCP Lease Renewal")
        print("3. Network Interface Restart")
        print("4. Router Reconnect")
        print("5. Mobile Hotspot")
        
        method_choice = input("Select method (1-5): ").strip()
        
        if method_choice == '1':
            changer.method_3_flush_dns_and_network()
        elif method_choice == '2':
            changer.method_2_renew_dhcp_lease()
        elif method_choice == '3':
            changer.method_1_restart_network_interface()
        elif method_choice == '4':
            changer.method_4_router_reconnect()
        elif method_choice == '5':
            changer.method_5_mobile_hotspot()
        
        changer.test_yahoo_finance_access()
        
    elif choice == '3':
        changer.test_yahoo_finance_access()
    elif choice == '4':
        changer.get_network_info()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
