#!/usr/bin/env python3
"""
Startup script for Dell iDRAC Fleet Emulator
"""

import subprocess
import sys
import os

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✓ AWS credentials configured for account: {identity['Account']}")
        return True
    except Exception as e:
        print(f"✗ AWS credentials not configured: {e}")
        return False

def main():
    print("Dell iDRAC Fleet Emulator Startup")
    print("=" * 40)
    
    # Check AWS credentials
    if not check_aws_credentials():
        print("\nPlease configure AWS credentials first:")
        print("  aws configure")
        print("  or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        sys.exit(1)
    
    print(f"✓ Starting emulator for 200 Dell servers")
    print(f"✓ Metrics will be published to CloudWatch namespace: Dell/iDRAC/Fleet")
    print(f"✓ Publishing interval: 60 seconds")
    print("\nPress Ctrl+C to stop the emulator\n")
    
    # Start the multi-server emulator
    try:
        subprocess.run([sys.executable, "multi_server_emulator.py"], check=True)
    except KeyboardInterrupt:
        print("\nEmulator stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running emulator: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
