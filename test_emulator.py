#!/usr/bin/env python3
"""
Test script for Dell iDRAC Emulator
Tests Redfish API, SNMP, and CloudWatch integration
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess
import time

# Configuration
REDFISH_URL = "http://localhost:5000"
REDFISH_USER = "root"
REDFISH_PASS = "calvin"
SNMP_HOST = "localhost"
SNMP_PORT = "1161"
SNMP_COMMUNITY = "public"

def test_redfish_api():
    """Test Redfish API endpoints"""
    print("\n" + "="*60)
    print("Testing Redfish API")
    print("="*60)
    
    auth = HTTPBasicAuth(REDFISH_USER, REDFISH_PASS)
    
    # Test service root
    print("\n1. Testing Service Root...")
    try:
        response = requests.get(f"{REDFISH_URL}/redfish/v1", auth=auth)
        if response.status_code == 200:
            print("✓ Service root accessible")
            data = response.json()
            print(f"  Redfish Version: {data.get('RedfishVersion')}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test thermal metrics
    print("\n2. Testing Thermal Metrics...")
    try:
        response = requests.get(
            f"{REDFISH_URL}/redfish/v1/Chassis/System.Embedded.1/Thermal",
            auth=auth
        )
        if response.status_code == 200:
            print("✓ Thermal metrics accessible")
            data = response.json()
            
            print("\n  Temperatures:")
            for temp in data.get('Temperatures', []):
                print(f"    - {temp['Name']}: {temp['ReadingCelsius']}°C")
            
            print("\n  Fans:")
            for fan in data.get('Fans', []):
                print(f"    - {fan['Name']}: {fan['Reading']} RPM")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test power metrics
    print("\n3. Testing Power Metrics...")
    try:
        response = requests.get(
            f"{REDFISH_URL}/redfish/v1/Chassis/System.Embedded.1/Power",
            auth=auth
        )
        if response.status_code == 200:
            print("✓ Power metrics accessible")
            data = response.json()
            
            for pc in data.get('PowerControl', []):
                print(f"  Power Consumed: {pc['PowerConsumedWatts']}W")
                print(f"  Power Available: {pc['PowerAvailableWatts']}W")
            
            print("\n  Power Supplies:")
            for ps in data.get('PowerSupplies', []):
                print(f"    - {ps['Name']}: {ps['Status']['Health']}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test status endpoint
    print("\n4. Testing Status Endpoint...")
    try:
        response = requests.get(f"{REDFISH_URL}/status")
        if response.status_code == 200:
            print("✓ Status endpoint accessible")
            data = response.json()
            print(f"  Server ID: {data.get('server_id')}")
            print(f"  CloudWatch Namespace: {data.get('cloudwatch_namespace')}")
            print("\n  Current Metrics:")
            for key, value in data.get('current_metrics', {}).items():
                print(f"    - {key}: {value}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_snmp():
    """Test SNMP agent"""
    print("\n" + "="*60)
    print("Testing SNMP Agent")
    print("="*60)
    
    # Dell OID base
    oids = {
        "CPU Temperature": "1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1.0",
        "Inlet Temperature": "1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.2.0",
        "Fan1 Speed": "1.3.6.1.4.1.674.10892.5.4.700.12.1.6.1.1.0",
        "Power Consumption": "1.3.6.1.4.1.674.10892.5.4.600.30.1.6.1.3.0",
        "System Status": "1.3.6.1.4.1.674.10892.5.4.200.10.1.4.1.0"
    }
    
    for name, oid in oids.items():
        print(f"\nTesting {name}...")
        try:
            cmd = [
                "snmpget", "-v2c", "-c", SNMP_COMMUNITY,
                f"{SNMP_HOST}:{SNMP_PORT}", oid
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"✓ {name}: {result.stdout.strip()}")
            else:
                print(f"✗ Failed: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout querying {name}")
        except FileNotFoundError:
            print("✗ snmpget command not found. Install net-snmp tools.")
            break
        except Exception as e:
            print(f"✗ Error: {str(e)}")

def test_snmp_walk():
    """Test SNMP walk on Dell OID tree"""
    print("\n" + "="*60)
    print("Testing SNMP Walk (Dell OID Tree)")
    print("="*60)
    
    try:
        cmd = [
            "snmpwalk", "-v2c", "-c", SNMP_COMMUNITY,
            f"{SNMP_HOST}:{SNMP_PORT}", "1.3.6.1.4.1.674"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ SNMP Walk successful")
            lines = result.stdout.strip().split('\n')
            print(f"  Found {len(lines)} OID entries")
            print("\n  Sample entries:")
            for line in lines[:5]:
                print(f"    {line}")
            if len(lines) > 5:
                print(f"    ... and {len(lines) - 5} more")
        else:
            print(f"✗ Failed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("✗ Timeout during SNMP walk")
    except FileNotFoundError:
        print("✗ snmpwalk command not found. Install net-snmp tools.")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("Usage Instructions")
    print("="*60)
    
    print("\n1. Start the Redfish API emulator:")
    print("   python idrac_emulator.py")
    
    print("\n2. Start the SNMP agent (in another terminal):")
    print("   python snmp_agent.py")
    
    print("\n3. Test Redfish API manually:")
    print(f"   curl -u {REDFISH_USER}:{REDFISH_PASS} {REDFISH_URL}/redfish/v1")
    print(f"   curl -u {REDFISH_USER}:{REDFISH_PASS} {REDFISH_URL}/redfish/v1/Chassis/System.Embedded.1/Thermal")
    
    print("\n4. Test SNMP manually:")
    print(f"   snmpget -v2c -c {SNMP_COMMUNITY} {SNMP_HOST}:{SNMP_PORT} 1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1.0")
    print(f"   snmpwalk -v2c -c {SNMP_COMMUNITY} {SNMP_HOST}:{SNMP_PORT} 1.3.6.1.4.1.674")
    
    print("\n5. CloudWatch Integration:")
    print("   - Metrics are automatically published every 60 seconds")
    print("   - Check AWS CloudWatch console under namespace: Dell/iDRAC/Emulated")
    print("   - Ensure AWS credentials are configured (aws configure)")
    
    print("\n6. Monitor CloudWatch metrics:")
    print("   aws cloudwatch list-metrics --namespace Dell/iDRAC/Emulated")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Dell iDRAC Emulator Test Suite")
    print("="*60)
    
    # Check if emulator is running
    try:
        response = requests.get(f"{REDFISH_URL}/status", timeout=2)
        if response.status_code == 200:
            print("\n✓ Emulator is running")
        else:
            print("\n✗ Emulator returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("\n✗ Emulator is not running!")
        print("\nPlease start the emulator first:")
        print("  python idrac_emulator.py")
        print("\nThen run this test script again.")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error connecting to emulator: {str(e)}")
        exit(1)
    
    # Run tests
    test_redfish_api()
    test_snmp()
    test_snmp_walk()
    print_usage_instructions()
    
    print("\n" + "="*60)
    print("Test Suite Completed")
    print("="*60 + "\n")
