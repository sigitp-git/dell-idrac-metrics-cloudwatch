#!/usr/bin/env python3
"""
Monitor Dell iDRAC Fleet Metrics in CloudWatch
"""

import boto3
from datetime import datetime, timedelta
import time

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def get_metric_statistics(metric_name, server_id=None):
    """Get recent statistics for a metric"""
    dimensions = []
    if server_id:
        dimensions.append({'Name': 'ServerID', 'Value': server_id})
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='Dell/iDRAC/Fleet',
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=datetime.utcnow() - timedelta(minutes=10),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average', 'Maximum', 'Minimum']
        )
        return response['Datapoints']
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return []

def list_available_metrics():
    """List all available metrics in the namespace"""
    try:
        response = cloudwatch.list_metrics(
            Namespace='Dell/iDRAC/Fleet'
        )
        return response['Metrics']
    except Exception as e:
        print(f"Error listing metrics: {e}")
        return []

def monitor_fleet():
    """Monitor fleet metrics"""
    print("Dell iDRAC Fleet Metrics Monitor")
    print("=" * 40)
    
    # Get available metrics
    metrics = list_available_metrics()
    if not metrics:
        print("No metrics found. Make sure the emulator is running.")
        return
    
    # Group metrics by type
    metric_names = set(m['MetricName'] for m in metrics)
    server_ids = set()
    for m in metrics:
        for dim in m['Dimensions']:
            if dim['Name'] == 'ServerID':
                server_ids.add(dim['Value'])
    
    print(f"Found {len(metric_names)} metric types across {len(server_ids)} servers")
    print(f"Metric types: {', '.join(sorted(metric_names))}")
    print(f"Sample servers: {', '.join(sorted(list(server_ids))[:5])}")
    
    # Monitor key metrics
    key_metrics = ['cpu1_temp', 'power_consumption', 'cpu_usage']
    
    while True:
        print(f"\n--- Metrics Update {datetime.now().strftime('%H:%M:%S')} ---")
        
        for metric in key_metrics:
            datapoints = get_metric_statistics(metric)
            if datapoints:
                latest = max(datapoints, key=lambda x: x['Timestamp'])
                print(f"{metric:15}: Avg={latest['Average']:6.1f}, Max={latest['Maximum']:6.1f}, Min={latest['Minimum']:6.1f}")
            else:
                print(f"{metric:15}: No recent data")
        
        time.sleep(30)

if __name__ == '__main__':
    try:
        monitor_fleet()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
