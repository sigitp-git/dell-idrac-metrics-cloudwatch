#!/usr/bin/env python3
"""
Dell iDRAC Multi-Server Metrics Emulator
Emulates 200 Dell servers publishing metrics to CloudWatch
"""

import json
import random
import time
from datetime import datetime
from threading import Thread
import boto3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Configuration
NUM_SERVERS = 200
CLOUDWATCH_NAMESPACE = "Dell/iDRAC/Fleet"
PUBLISH_INTERVAL = 60  # seconds

class ServerMetricsGenerator:
    """Generate realistic metrics for a single server"""
    
    def __init__(self, server_id):
        self.server_id = server_id
        # Each server has slightly different baseline characteristics
        self.base_cpu_temp = random.uniform(40, 50)
        self.base_power = random.uniform(200, 400)
        self.base_fan_speed = random.randint(2500, 4000)
        
    def get_all_metrics(self):
        """Get all metrics for this server"""
        return {
            'cpu1_temp': round(self.base_cpu_temp + random.uniform(-5, 15), 1),
            'cpu2_temp': round(self.base_cpu_temp + random.uniform(-5, 15), 1),
            'inlet_temp': round(random.uniform(20, 35), 1),
            'exhaust_temp': round(random.uniform(30, 50), 1),
            'fan1_speed': max(2000, self.base_fan_speed + random.randint(-500, 1000)),
            'fan2_speed': max(2000, self.base_fan_speed + random.randint(-500, 1000)),
            'power_consumption': round(self.base_power + random.uniform(-50, 100), 2),
            'cpu_usage': round(random.uniform(10, 85), 2),
            'memory_usage': round(random.uniform(30, 75), 2),
            'disk_temp': round(random.uniform(25, 55), 1)
        }

class MultiServerCloudWatchPublisher:
    """Publish metrics for multiple servers to CloudWatch"""
    
    def __init__(self, num_servers=NUM_SERVERS):
        self.namespace = CLOUDWATCH_NAMESPACE
        self.servers = {}
        
        # Initialize server generators
        for i in range(1, num_servers + 1):
            server_id = f"DELL-SRV-{i:03d}"
            self.servers[server_id] = ServerMetricsGenerator(server_id)
        
        logger.info(f"Initialized {len(self.servers)} server emulators")
    
    def collect_all_metrics(self):
        """Collect metrics from all servers"""
        all_metrics = []
        
        for server_id, generator in self.servers.items():
            server_metrics = generator.get_all_metrics()
            
            # Convert to CloudWatch format
            for metric_name, value in server_metrics.items():
                all_metrics.append({
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': 'Percent' if 'usage' in metric_name else 'None',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'ServerID', 'Value': server_id},
                        {'Name': 'MetricType', 'Value': self._get_metric_type(metric_name)}
                    ]
                })
        
        return all_metrics
    
    def _get_metric_type(self, metric_name):
        """Categorize metric type"""
        if 'temp' in metric_name:
            return 'Thermal'
        elif 'fan' in metric_name:
            return 'Cooling'
        elif 'power' in metric_name:
            return 'Power'
        elif 'usage' in metric_name:
            return 'Performance'
        else:
            return 'General'
    
    def publish_metrics_batch(self, metrics_batch):
        """Publish a batch of metrics to CloudWatch"""
        try:
            cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=metrics_batch
            )
            return True
        except Exception as e:
            logger.error(f"Error publishing batch: {str(e)}")
            return False
    
    def publish_all_metrics(self):
        """Collect and publish all server metrics"""
        logger.info("Collecting metrics from all servers...")
        all_metrics = self.collect_all_metrics()
        
        # CloudWatch accepts max 20 metrics per request
        batch_size = 20
        total_batches = len(all_metrics) // batch_size + (1 if len(all_metrics) % batch_size else 0)
        successful_batches = 0
        
        for i in range(0, len(all_metrics), batch_size):
            batch = all_metrics[i:i+batch_size]
            if self.publish_metrics_batch(batch):
                successful_batches += 1
        
        logger.info(f"Published {successful_batches}/{total_batches} batches ({len(all_metrics)} total metrics)")
        return successful_batches == total_batches

def publisher_loop():
    """Main publishing loop"""
    publisher = MultiServerCloudWatchPublisher()
    logger.info(f"Starting metrics publishing for {NUM_SERVERS} servers")
    logger.info(f"Publishing to CloudWatch namespace: {CLOUDWATCH_NAMESPACE}")
    logger.info(f"Publish interval: {PUBLISH_INTERVAL} seconds")
    
    while True:
        try:
            start_time = time.time()
            success = publisher.publish_all_metrics()
            duration = time.time() - start_time
            
            if success:
                logger.info(f"Successfully published all metrics in {duration:.2f} seconds")
            else:
                logger.warning("Some metric batches failed to publish")
            
            time.sleep(PUBLISH_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Shutting down metrics publisher...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in publisher loop: {str(e)}")
            time.sleep(PUBLISH_INTERVAL)

if __name__ == '__main__':
    logger.info("Dell iDRAC Multi-Server Metrics Emulator")
    logger.info("=" * 50)
    
    try:
        publisher_loop()
    except KeyboardInterrupt:
        logger.info("Emulator stopped by user")
