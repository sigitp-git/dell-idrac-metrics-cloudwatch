#!/usr/bin/env python3
"""
Dell iDRAC Metrics Emulator
Provides Redfish API and SNMP endpoints with CloudWatch integration
"""

import json
import random
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import boto3
from threading import Thread
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for Redfish API
app = Flask(__name__)
auth = HTTPBasicAuth()

# CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Configuration
SERVER_ID = "emulated-server-001"
CLOUDWATCH_NAMESPACE = "Dell/iDRAC/Emulated"

# Simulated metrics storage
class MetricsGenerator:
    """Generate realistic iDRAC metrics"""
    
    def __init__(self):
        self.base_cpu_temp = 45.0
        self.base_power = 250.0
        self.base_fan_speed = 3000
        
    def get_cpu_temperature(self, cpu_id=1):
        """Generate CPU temperature (40-85°C)"""
        variation = random.uniform(-5, 15)
        return round(self.base_cpu_temp + variation, 1)
    
    def get_memory_temperature(self, dimm_id=1):
        """Generate memory temperature (35-65°C)"""
        return round(random.uniform(35, 65), 1)
    
    def get_inlet_temperature(self):
        """Generate inlet temperature (20-35°C)"""
        return round(random.uniform(20, 35), 1)
    
    def get_exhaust_temperature(self):
        """Generate exhaust temperature (30-50°C)"""
        return round(random.uniform(30, 50), 1)
    
    def get_fan_speed(self, fan_id=1):
        """Generate fan speed (2000-8000 RPM)"""
        variation = random.randint(-1000, 2000)
        return max(2000, self.base_fan_speed + variation)
    
    def get_power_consumption(self):
        """Generate power consumption (200-600W)"""
        variation = random.uniform(-50, 150)
        return round(self.base_power + variation, 2)
    
    def get_cpu_usage(self):
        """Generate CPU usage (0-100%)"""
        return round(random.uniform(10, 85), 2)
    
    def get_memory_usage(self):
        """Generate memory usage (0-100%)"""
        return round(random.uniform(30, 75), 2)
    
    def get_disk_temperature(self, disk_id=0):
        """Generate disk temperature (25-55°C)"""
        return round(random.uniform(25, 55), 1)
    
    def get_network_throughput(self):
        """Generate network throughput (Mbps)"""
        return round(random.uniform(10, 1000), 2)

metrics_gen = MetricsGenerator()

# Authentication for Redfish API
users = {
    "root": "calvin",
    "admin": "admin123"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

# Redfish API Endpoints
@app.route('/redfish/v1')
@auth.login_required
def redfish_root():
    """Redfish service root"""
    return jsonify({
        "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
        "@odata.id": "/redfish/v1",
        "@odata.type": "#ServiceRoot.v1_5_0.ServiceRoot",
        "Id": "RootService",
        "Name": "Root Service",
        "RedfishVersion": "1.6.0",
        "UUID": "12345678-1234-1234-1234-123456789012",
        "Chassis": {
            "@odata.id": "/redfish/v1/Chassis"
        },
        "Systems": {
            "@odata.id": "/redfish/v1/Systems"
        },
        "TelemetryService": {
            "@odata.id": "/redfish/v1/TelemetryService"
        }
    })

@app.route('/redfish/v1/Chassis')
@auth.login_required
def chassis_collection():
    """Chassis collection"""
    return jsonify({
        "@odata.context": "/redfish/v1/$metadata#ChassisCollection.ChassisCollection",
        "@odata.id": "/redfish/v1/Chassis",
        "@odata.type": "#ChassisCollection.ChassisCollection",
        "Name": "Chassis Collection",
        "Members": [
            {"@odata.id": "/redfish/v1/Chassis/System.Embedded.1"}
        ],
        "Members@odata.count": 1
    })

@app.route('/redfish/v1/Chassis/System.Embedded.1/Thermal')
@auth.login_required
def thermal_metrics():
    """Thermal metrics endpoint"""
    return jsonify({
        "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
        "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal",
        "@odata.type": "#Thermal.v1_5_0.Thermal",
        "Id": "Thermal",
        "Name": "Thermal",
        "Temperatures": [
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Temperatures/0",
                "MemberId": "0",
                "Name": "CPU1 Temp",
                "SensorNumber": 1,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": metrics_gen.get_cpu_temperature(1),
                "UpperThresholdNonCritical": 75,
                "UpperThresholdCritical": 85,
                "UpperThresholdFatal": 95,
                "MinReadingRangeTemp": 0,
                "MaxReadingRangeTemp": 100
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Temperatures/1",
                "MemberId": "1",
                "Name": "CPU2 Temp",
                "SensorNumber": 2,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": metrics_gen.get_cpu_temperature(2),
                "UpperThresholdNonCritical": 75,
                "UpperThresholdCritical": 85,
                "UpperThresholdFatal": 95
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Temperatures/2",
                "MemberId": "2",
                "Name": "System Board Inlet Temp",
                "SensorNumber": 3,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": metrics_gen.get_inlet_temperature(),
                "UpperThresholdNonCritical": 35,
                "UpperThresholdCritical": 40,
                "UpperThresholdFatal": 45
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Temperatures/3",
                "MemberId": "3",
                "Name": "System Board Exhaust Temp",
                "SensorNumber": 4,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": metrics_gen.get_exhaust_temperature(),
                "UpperThresholdNonCritical": 70,
                "UpperThresholdCritical": 75,
                "UpperThresholdFatal": 80
            }
        ],
        "Fans": [
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Fans/0",
                "MemberId": "0",
                "Name": "System Board Fan1A",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "Reading": metrics_gen.get_fan_speed(1),
                "ReadingUnits": "RPM",
                "LowerThresholdNonCritical": 2000,
                "LowerThresholdCritical": 1500,
                "MinReadingRange": 0,
                "MaxReadingRange": 10000
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Fans/1",
                "MemberId": "1",
                "Name": "System Board Fan1B",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "Reading": metrics_gen.get_fan_speed(2),
                "ReadingUnits": "RPM",
                "LowerThresholdNonCritical": 2000,
                "LowerThresholdCritical": 1500
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal#/Fans/2",
                "MemberId": "2",
                "Name": "System Board Fan2A",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "Reading": metrics_gen.get_fan_speed(3),
                "ReadingUnits": "RPM",
                "LowerThresholdNonCritical": 2000,
                "LowerThresholdCritical": 1500
            }
        ]
    })

@app.route('/redfish/v1/Chassis/System.Embedded.1/Power')
@auth.login_required
def power_metrics():
    """Power metrics endpoint"""
    power_consumption = metrics_gen.get_power_consumption()
    
    return jsonify({
        "@odata.context": "/redfish/v1/$metadata#Power.Power",
        "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Power",
        "@odata.type": "#Power.v1_5_0.Power",
        "Id": "Power",
        "Name": "Power",
        "PowerControl": [
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Power#/PowerControl/0",
                "MemberId": "0",
                "Name": "System Power Control",
                "PowerConsumedWatts": power_consumption,
                "PowerRequestedWatts": power_consumption + 50,
                "PowerAvailableWatts": 750,
                "PowerCapacityWatts": 750,
                "PowerAllocatedWatts": 750,
                "PowerMetrics": {
                    "IntervalInMin": 1,
                    "MinConsumedWatts": 200,
                    "MaxConsumedWatts": 600,
                    "AverageConsumedWatts": power_consumption
                },
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                }
            }
        ],
        "PowerSupplies": [
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Power#/PowerSupplies/0",
                "MemberId": "0",
                "Name": "PS1 Status",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "PowerSupplyType": "AC",
                "LineInputVoltageType": "ACHighLine",
                "LineInputVoltage": 230,
                "PowerCapacityWatts": 750,
                "LastPowerOutputWatts": power_consumption / 2,
                "Model": "PWR SPLY,750W,RDNT,ARTESYN",
                "Manufacturer": "DELL",
                "FirmwareVersion": "00.1A.2B"
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Power#/PowerSupplies/1",
                "MemberId": "1",
                "Name": "PS2 Status",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "PowerSupplyType": "AC",
                "LineInputVoltageType": "ACHighLine",
                "LineInputVoltage": 230,
                "PowerCapacityWatts": 750,
                "LastPowerOutputWatts": power_consumption / 2,
                "Model": "PWR SPLY,750W,RDNT,ARTESYN",
                "Manufacturer": "DELL",
                "FirmwareVersion": "00.1A.2B"
            }
        ]
    })

@app.route('/redfish/v1/TelemetryService/MetricDefinitions')
@auth.login_required
def metric_definitions():
    """Telemetry metric definitions"""
    return jsonify({
        "@odata.context": "/redfish/v1/$metadata#MetricDefinitionCollection.MetricDefinitionCollection",
        "@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions",
        "@odata.type": "#MetricDefinitionCollection.MetricDefinitionCollection",
        "Name": "Metric Definition Collection",
        "Members": [
            {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/CPUTemp"},
            {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/FanSpeed"},
            {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/PowerConsumption"},
            {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/CPUUsage"},
            {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/MemoryUsage"}
        ],
        "Members@odata.count": 5
    })

# CloudWatch Integration
class CloudWatchPublisher:
    """Publish metrics to AWS CloudWatch"""
    
    def __init__(self, namespace=CLOUDWATCH_NAMESPACE, server_id=SERVER_ID):
        self.namespace = namespace
        self.server_id = server_id
        self.enabled = True
        
    def publish_metrics(self, metrics_data):
        """Publish batch of metrics to CloudWatch"""
        if not self.enabled:
            return
        
        try:
            metric_data = []
            
            for metric in metrics_data:
                metric_data.append({
                    'MetricName': metric['name'],
                    'Value': metric['value'],
                    'Unit': metric.get('unit', 'None'),
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'ServerID', 'Value': self.server_id},
                        {'Name': 'MetricType', 'Value': metric.get('type', 'General')}
                    ]
                })
            
            # CloudWatch accepts max 20 metrics per request
            for i in range(0, len(metric_data), 20):
                batch = metric_data[i:i+20]
                cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )
                logger.info(f"Published {len(batch)} metrics to CloudWatch")
                
        except Exception as e:
            logger.error(f"Error publishing to CloudWatch: {str(e)}")
    
    def collect_and_publish(self):
        """Collect all metrics and publish to CloudWatch"""
        metrics_data = [
            {
                'name': 'CPU1_Temperature',
                'value': metrics_gen.get_cpu_temperature(1),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'CPU2_Temperature',
                'value': metrics_gen.get_cpu_temperature(2),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Inlet_Temperature',
                'value': metrics_gen.get_inlet_temperature(),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Exhaust_Temperature',
                'value': metrics_gen.get_exhaust_temperature(),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Fan1_Speed',
                'value': metrics_gen.get_fan_speed(1),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Fan2_Speed',
                'value': metrics_gen.get_fan_speed(2),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Fan3_Speed',
                'value': metrics_gen.get_fan_speed(3),
                'unit': 'None',
                'type': 'Thermal'
            },
            {
                'name': 'Power_Consumption',
                'value': metrics_gen.get_power_consumption(),
                'unit': 'None',
                'type': 'Power'
            },
            {
                'name': 'CPU_Usage',
                'value': metrics_gen.get_cpu_usage(),
                'unit': 'Percent',
                'type': 'Performance'
            },
            {
                'name': 'Memory_Usage',
                'value': metrics_gen.get_memory_usage(),
                'unit': 'Percent',
                'type': 'Performance'
            }
        ]
        
        self.publish_metrics(metrics_data)

cw_publisher = CloudWatchPublisher()

def cloudwatch_publisher_loop():
    """Background thread for periodic CloudWatch publishing"""
    logger.info("CloudWatch publisher thread started")
    while True:
        try:
            cw_publisher.collect_and_publish()
            time.sleep(60)  # Publish every 60 seconds
        except Exception as e:
            logger.error(f"Error in CloudWatch publisher loop: {str(e)}")
            time.sleep(60)

# Status endpoint
@app.route('/status')
def status():
    """Emulator status endpoint"""
    return jsonify({
        "status": "running",
        "server_id": SERVER_ID,
        "cloudwatch_namespace": CLOUDWATCH_NAMESPACE,
        "endpoints": {
            "redfish_root": "/redfish/v1",
            "thermal": "/redfish/v1/Chassis/System.Embedded.1/Thermal",
            "power": "/redfish/v1/Chassis/System.Embedded.1/Power",
            "metrics": "/redfish/v1/TelemetryService/MetricDefinitions"
        },
        "authentication": {
            "username": "root",
            "password": "calvin"
        },
        "current_metrics": {
            "cpu1_temp": metrics_gen.get_cpu_temperature(1),
            "cpu2_temp": metrics_gen.get_cpu_temperature(2),
            "inlet_temp": metrics_gen.get_inlet_temperature(),
            "power_watts": metrics_gen.get_power_consumption(),
            "fan1_rpm": metrics_gen.get_fan_speed(1)
        }
    })

if __name__ == '__main__':
    logger.info("Starting Dell iDRAC Emulator")
    logger.info(f"Server ID: {SERVER_ID}")
    logger.info(f"CloudWatch Namespace: {CLOUDWATCH_NAMESPACE}")
    
    # Start CloudWatch publisher thread
    cw_thread = Thread(target=cloudwatch_publisher_loop, daemon=True)
    cw_thread.start()
    
    # Start Flask app
    logger.info("Starting Redfish API server on http://0.0.0.0:5000")
    logger.info("Default credentials - Username: root, Password: calvin")
    app.run(host='0.0.0.0', port=5000, debug=False)
