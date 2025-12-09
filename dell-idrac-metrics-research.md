# Dell iDRAC Low-Level Metrics Research Report

## Overview

Dell iDRAC (Integrated Dell Remote Access Controller) provides comprehensive telemetry capabilities for monitoring low-level hardware metrics on PowerEdge servers. This report details the available metrics, access methods, and documentation resources.

## Requirements

- **License**: iDRAC Datacenter license required
- **Platform**: 14th generation (14G) or newer PowerEdge servers
- **Feature**: Telemetry data collection and streaming

## Documentation Sources

### Official Dell Documentation

The **Dell iDRAC Telemetry Reference Guide** is the definitive source for all available metrics. This platform-specific guide can be accessed through:

- Dell Support website (search for your specific server model)
- Platform-specific versions available for different PowerEdge generations

### Redfish API Access

Metrics are exposed via the Redfish standard API. Query available metrics using:

```
GET https://<iDRAC_IP>/redfish/v1/TelemetryService/MetricDefinitions
```

Each MetricDefinition entry includes:
- Description
- Type
- Units (Celsius, RPM, Percentage, etc.)
- Sensing interval

### GitHub Resources

Dell provides reference tools and sample implementations:
- Reference scripts for data collection pipelines
- Sample metric definitions
- Integration examples

## Access Methods

Metrics can be accessed through three primary interfaces:

1. **iDRAC Web Interface** - GUI-based monitoring
2. **RACADM** - Command-line administration tool
3. **Redfish API** - RESTful API for programmatic access

## Available Metric Categories

### CPU and Memory Metrics

- CPU usage percentage
- Core frequency
- Energy consumption
- Temperature readings
- ECC errors (correctable and uncorrectable)

### Power and Thermal Metrics

- System input/output power
- Component-level power consumption:
  - CPU power
  - Memory power
  - Storage power
- Fan speeds (RPM)
- Temperature sensors:
  - Inlet temperature
  - Exhaust temperature
  - CPU temperature
  - GPU temperature

### Storage Metrics

**SMART Data** for SAS/SATA and NVMe drives:
- Drive temperature
- Power-on hours
- Error counts
- Drive life remaining (percentage)
- Read/write statistics

### Network Metrics

**NIC Statistics**:
- Link status
- Packet counts:
  - Unicast packets
  - Multicast packets
  - Error packets
- Fiber Channel port statistics

### Accelerator Metrics (GPU/FPGA)

- GPU usage percentage
- Memory usage
- Clock frequencies
- Power consumption

### Chassis and Environmental Metrics

- Cumulative system usage percentages:
  - CPU usage
  - I/O usage
  - Memory usage
- Voltage readings
- Amperage readings
- General environmental sensors

## Integration and Implementation

### Redfish Property URIs

The documentation maps raw metric values to specific Redfish property URIs, enabling:
- Custom data collection pipelines
- Integration with analytics platforms
- Automated monitoring solutions
- Third-party tool integration

### SNMP Integration

Dell iDRAC supports SNMP (Simple Network Management Protocol) for accessing hardware metrics, providing compatibility with traditional network monitoring systems.

#### SNMP Configuration

**Enabling SNMP on iDRAC**:
1. Access iDRAC web interface
2. Navigate to: **iDRAC Settings → Network → SNMP Agent**
3. Enable SNMP Agent
4. Configure SNMP settings:
   - SNMP v1/v2c: Set community strings (default: public)
   - SNMP v3: Configure users, authentication, and privacy protocols

**SNMP Versions Supported**:
- SNMPv1 - Basic, unencrypted
- SNMPv2c - Community-based with improved error handling
- SNMPv3 - Secure with authentication and encryption (recommended)

#### Dell MIBs (Management Information Bases)

Dell provides proprietary MIBs for accessing iDRAC metrics:

**Key MIB Files**:
- `IDRAC-MIB-SMIv2.mib` - Core iDRAC management
- `10892.mib` - Dell Server Administrator MIB
- `DELL-RAC-MIB.mib` - Remote Access Controller specific

**Download Location**:
- Available from Dell Support website
- Bundled with Dell OpenManage Server Administrator
- Can be exported directly from iDRAC interface

#### Accessible Metrics via SNMP

SNMP provides access to many of the same low-level metrics:

**System Health**:
- Overall system status
- Component health status (power supplies, fans, memory, CPUs)

**Temperature Sensors**:
- Chassis inlet/exhaust temperatures
- CPU temperatures
- Memory temperatures

**Power Metrics**:
- System power consumption (watts)
- Power supply status and redundancy
- Amperage readings

**Fan Metrics**:
- Fan speeds (RPM)
- Fan health status

**Storage**:
- Physical disk status
- RAID controller status
- Virtual disk status

**Memory**:
- Memory module status
- ECC error counts

**Network**:
- NIC status and statistics

#### SNMP Query Examples

**Using snmpwalk** (Linux/Unix):
```bash
# Query all Dell enterprise OID metrics
snmpwalk -v2c -c public <iDRAC_IP> 1.3.6.1.4.1.674

# Query system chassis status
snmpget -v2c -c public <iDRAC_IP> 1.3.6.1.4.1.674.10892.5.4.200.10.1.4.1

# Query power consumption
snmpget -v2c -c public <iDRAC_IP> 1.3.6.1.4.1.674.10892.5.4.600.30.1.6.1.3
```

**Using SNMPv3** (secure):
```bash
snmpwalk -v3 -l authPriv -u <username> -a SHA -A <auth_password> \
  -x AES -X <priv_password> <iDRAC_IP> 1.3.6.1.4.1.674
```

#### SNMP Traps

iDRAC can send SNMP traps for proactive alerting:

**Configuration**:
1. Navigate to: **iDRAC Settings → Network → SNMP Trap Destination**
2. Add trap destination IP addresses
3. Configure alert policies for specific events

**Trap Categories**:
- Critical hardware failures
- Temperature threshold violations
- Power supply failures
- Fan failures
- Storage events
- System events (boot, shutdown, crashes)

#### Integration with Monitoring Tools

SNMP enables integration with popular monitoring platforms:

**Compatible Tools**:
- Nagios/Icinga
- Zabbix
- PRTG Network Monitor
- SolarWinds
- Prometheus (via SNMP exporter)
- Cacti
- LibreNMS

**Integration Benefits**:
- Centralized monitoring dashboard
- Historical data collection
- Alerting and notification
- Trend analysis
- Multi-vendor environment support

#### SNMP vs Redfish Comparison

| Feature | SNMP | Redfish |
|---------|------|---------|
| Protocol | UDP-based | HTTP/HTTPS RESTful |
| Data Format | ASN.1/BER | JSON |
| Security | SNMPv3 encryption | TLS/SSL |
| Bandwidth | Lightweight | More verbose |
| Standardization | Industry standard | Modern standard |
| Ease of Use | Requires MIB files | Self-documenting API |
| Real-time Streaming | Polling-based | Supports SSE/WebSocket |
| Legacy Support | Excellent | Limited to modern systems |

**Recommendation**: Use Redfish for modern integrations and detailed telemetry streaming. Use SNMP for legacy system compatibility and integration with existing SNMP-based monitoring infrastructure.

## Amazon CloudWatch Integration

AWS CloudWatch does not have native, direct integration with Redfish or SNMP protocols. However, there are several effective approaches to ingest Dell iDRAC metrics into CloudWatch.

### Integration Architecture Options

#### Option 1: Custom CloudWatch Agent with Redfish Collector

**Architecture**:
```
iDRAC (Redfish API) → Custom Collector Script → CloudWatch Agent → CloudWatch
```

**Implementation Steps**:

1. **Create a Redfish Collector Script** (Python example):

```python
import requests
import boto3
from datetime import datetime
import json

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def collect_idrac_metrics(idrac_ip, username, password):
    """Collect metrics from iDRAC via Redfish API"""
    base_url = f"https://{idrac_ip}/redfish/v1"
    auth = (username, password)
    
    # Disable SSL warnings for self-signed certs (use proper certs in production)
    requests.packages.urllib3.disable_warnings()
    
    # Get thermal metrics
    thermal_url = f"{base_url}/Chassis/System.Embedded.1/Thermal"
    response = requests.get(thermal_url, auth=auth, verify=False)
    thermal_data = response.json()
    
    metrics = []
    
    # Parse temperature sensors
    for temp in thermal_data.get('Temperatures', []):
        metrics.append({
            'MetricName': f"Temperature_{temp['Name'].replace(' ', '_')}",
            'Value': temp['ReadingCelsius'],
            'Unit': 'None',
            'Timestamp': datetime.utcnow(),
            'Dimensions': [
                {'Name': 'ServerID', 'Value': idrac_ip},
                {'Name': 'SensorName', 'Value': temp['Name']}
            ]
        })
    
    # Parse fan speeds
    for fan in thermal_data.get('Fans', []):
        metrics.append({
            'MetricName': f"FanSpeed_{fan['Name'].replace(' ', '_')}",
            'Value': fan['Reading'],
            'Unit': 'None',
            'Dimensions': [
                {'Name': 'ServerID', 'Value': idrac_ip},
                {'Name': 'FanName', 'Value': fan['Name']}
            ]
        })
    
    # Get power metrics
    power_url = f"{base_url}/Chassis/System.Embedded.1/Power"
    response = requests.get(power_url, auth=auth, verify=False)
    power_data = response.json()
    
    # Parse power consumption
    for power_control in power_data.get('PowerControl', []):
        if 'PowerConsumedWatts' in power_control:
            metrics.append({
                'MetricName': 'PowerConsumption',
                'Value': power_control['PowerConsumedWatts'],
                'Unit': 'None',
                'Dimensions': [
                    {'Name': 'ServerID', 'Value': idrac_ip}
                ]
            })
    
    return metrics

def publish_to_cloudwatch(metrics, namespace='Dell/iDRAC'):
    """Publish metrics to CloudWatch"""
    # CloudWatch accepts max 20 metrics per request
    for i in range(0, len(metrics), 20):
        batch = metrics[i:i+20]
        cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=batch
        )
        print(f"Published {len(batch)} metrics to CloudWatch")

# Main execution
if __name__ == "__main__":
    idrac_servers = [
        {'ip': '10.0.1.100', 'username': 'root', 'password': 'password'},
        {'ip': '10.0.1.101', 'username': 'root', 'password': 'password'}
    ]
    
    for server in idrac_servers:
        metrics = collect_idrac_metrics(
            server['ip'], 
            server['username'], 
            server['password']
        )
        publish_to_cloudwatch(metrics)
```

2. **Deploy as Lambda Function** (scheduled via EventBridge):

```python
# lambda_function.py
import os
import json
from collector import collect_idrac_metrics, publish_to_cloudwatch

def lambda_handler(event, context):
    """Lambda handler for scheduled metric collection"""
    # Store credentials in AWS Secrets Manager
    servers = json.loads(os.environ['IDRAC_SERVERS'])
    
    for server in servers:
        try:
            metrics = collect_idrac_metrics(
                server['ip'],
                server['username'],
                server['password']
            )
            publish_to_cloudwatch(metrics)
        except Exception as e:
            print(f"Error collecting from {server['ip']}: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Metrics collection completed')
    }
```

3. **Schedule with EventBridge**:
   - Create EventBridge rule with rate expression: `rate(1 minute)` or `rate(5 minutes)`
   - Target: Lambda function created above

#### Option 2: EC2 Instance with CloudWatch Agent + SNMP

**Architecture**:
```
iDRAC (SNMP) → EC2 Collector Instance → CloudWatch Agent → CloudWatch
```

**Implementation Steps**:

1. **Launch EC2 Instance** (Amazon Linux 2 or Ubuntu)

2. **Install SNMP Tools and CloudWatch Agent**:

```bash
# Install SNMP tools
sudo yum install net-snmp net-snmp-utils -y  # Amazon Linux
# or
sudo apt-get install snmp snmp-mibs-downloader -y  # Ubuntu

# Install CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -i amazon-cloudwatch-agent.rpm
```

3. **Create SNMP Collection Script**:

```bash
#!/bin/bash
# snmp_to_cloudwatch.sh

IDRAC_IP="10.0.1.100"
COMMUNITY="public"
NAMESPACE="Dell/iDRAC"
REGION="us-east-1"

# Collect CPU temperature
CPU_TEMP=$(snmpget -v2c -c $COMMUNITY $IDRAC_IP 1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1 | awk '{print $NF}')

# Collect system power consumption
POWER=$(snmpget -v2c -c $COMMUNITY $IDRAC_IP 1.3.6.1.4.1.674.10892.5.4.600.30.1.6.1.3 | awk '{print $NF}')

# Collect fan speed
FAN_SPEED=$(snmpget -v2c -c $COMMUNITY $IDRAC_IP 1.3.6.1.4.1.674.10892.5.4.700.12.1.6.1.1 | awk '{print $NF}')

# Publish to CloudWatch
aws cloudwatch put-metric-data \
  --namespace "$NAMESPACE" \
  --metric-name "CPUTemperature" \
  --value "$CPU_TEMP" \
  --dimensions ServerID=$IDRAC_IP \
  --region $REGION

aws cloudwatch put-metric-data \
  --namespace "$NAMESPACE" \
  --metric-name "PowerConsumption" \
  --value "$POWER" \
  --dimensions ServerID=$IDRAC_IP \
  --region $REGION

aws cloudwatch put-metric-data \
  --namespace "$NAMESPACE" \
  --metric-name "FanSpeed" \
  --value "$FAN_SPEED" \
  --dimensions ServerID=$IDRAC_IP \
  --region $REGION
```

4. **Schedule with Cron**:

```bash
# Edit crontab
crontab -e

# Add entry to run every minute
* * * * * /path/to/snmp_to_cloudwatch.sh >> /var/log/snmp_collector.log 2>&1
```

#### Option 3: Prometheus + CloudWatch Exporter

**Architecture**:
```
iDRAC (Redfish/SNMP) → Prometheus → CloudWatch Exporter → CloudWatch
```

**Implementation Steps**:

1. **Deploy Prometheus with Redfish Exporter**:

```yaml
# prometheus.yml
global:
  scrape_interval: 60s

scrape_configs:
  - job_name: 'idrac'
    static_configs:
      - targets: ['localhost:9610']
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9610
```

2. **Use Redfish Exporter for Prometheus**:

```bash
# Run Redfish exporter (available on GitHub)
docker run -d -p 9610:9610 \
  -e IDRAC_HOST=10.0.1.100 \
  -e IDRAC_USER=root \
  -e IDRAC_PASSWORD=password \
  jenningsloy318/redfish_exporter
```

3. **Deploy CloudWatch Exporter**:

```bash
# Install cloudwatch_exporter
docker run -d -p 9106:9106 \
  -v /path/to/config.yml:/config/config.yml \
  prom/cloudwatch-exporter
```

4. **Configure Prometheus Remote Write to CloudWatch**:

Use AWS Managed Prometheus (AMP) with automatic CloudWatch integration, or use third-party tools like Grafana Agent.

#### Option 4: AWS IoT Core Integration

**Architecture**:
```
iDRAC → Edge Device/Gateway → AWS IoT Core → CloudWatch
```

**Use Case**: For on-premises Dell servers with limited AWS connectivity

**Implementation**:
- Deploy AWS IoT Greengrass on edge device
- Create component to collect iDRAC metrics
- Publish to IoT Core topics
- Use IoT Rules to route to CloudWatch

### CloudWatch Metric Namespace Design

Organize metrics using hierarchical namespaces:

```
Dell/iDRAC/Thermal/Temperature
Dell/iDRAC/Thermal/FanSpeed
Dell/iDRAC/Power/Consumption
Dell/iDRAC/Power/Redundancy
Dell/iDRAC/Storage/DiskHealth
Dell/iDRAC/Storage/RAIDStatus
Dell/iDRAC/Memory/ECCErrors
Dell/iDRAC/CPU/Usage
Dell/iDRAC/CPU/Temperature
```

### CloudWatch Dimensions Strategy

Use dimensions for filtering and aggregation:

```python
dimensions = [
    {'Name': 'ServerID', 'Value': 'server-001'},
    {'Name': 'DataCenter', 'Value': 'us-east-1a'},
    {'Name': 'Environment', 'Value': 'production'},
    {'Name': 'ServerModel', 'Value': 'PowerEdge-R750'},
    {'Name': 'ComponentType', 'Value': 'CPU'},
    {'Name': 'ComponentID', 'Value': 'CPU.Socket.1'}
]
```

### CloudWatch Alarms Configuration

Create alarms for critical metrics:

```bash
# CPU Temperature alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "iDRAC-High-CPU-Temp" \
  --alarm-description "Alert when CPU temperature exceeds 80C" \
  --namespace "Dell/iDRAC" \
  --metric-name "CPUTemperature" \
  --dimensions Name=ServerID,Value=server-001 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Power consumption alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "iDRAC-High-Power-Usage" \
  --alarm-description "Alert when power exceeds 500W" \
  --namespace "Dell/iDRAC" \
  --metric-name "PowerConsumption" \
  --dimensions Name=ServerID,Value=server-001 \
  --statistic Average \
  --period 300 \
  --threshold 500 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3
```

### Cost Considerations

**CloudWatch Pricing Factors**:
- Custom metrics: $0.30 per metric per month (first 10,000 metrics)
- API requests: $0.01 per 1,000 PutMetricData requests
- Alarms: $0.10 per alarm per month (first 10 alarms free)

**Cost Optimization**:
- Aggregate metrics before publishing (reduce metric count)
- Use appropriate collection intervals (1-5 minutes for most use cases)
- Implement metric filtering (only send critical metrics)
- Use high-resolution metrics only when necessary

### Security Best Practices

1. **Credentials Management**:
   - Store iDRAC credentials in AWS Secrets Manager
   - Rotate credentials regularly
   - Use IAM roles for EC2/Lambda instead of access keys

2. **Network Security**:
   - Use VPC endpoints for CloudWatch API calls
   - Implement security groups to restrict iDRAC access
   - Use VPN or Direct Connect for on-premises servers

3. **Encryption**:
   - Enable encryption in transit (TLS for Redfish, SNMPv3)
   - Use encrypted connections to CloudWatch

### Monitoring and Troubleshooting

**CloudWatch Logs Integration**:
```python
import logging
import watchtower

# Configure logging to CloudWatch Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group='/dell/idrac/collector',
    stream_name='metric-collection'
))

# Log collection activities
logger.info(f"Collected {len(metrics)} metrics from {idrac_ip}")
logger.error(f"Failed to collect from {idrac_ip}: {error}")
```

**Recommended Dashboards**:
- Server health overview (all servers)
- Thermal monitoring (temperatures, fan speeds)
- Power consumption trends
- Storage health status
- Alert history and response times

### Integration Comparison

| Approach | Complexity | Cost | Scalability | Real-time | Best For |
|----------|-----------|------|-------------|-----------|----------|
| Lambda + Redfish | Medium | Low | High | Near real-time | Cloud-native, serverless |
| EC2 + SNMP | Low | Medium | Medium | Real-time | Legacy integration |
| Prometheus + Exporter | High | Medium | High | Real-time | Existing Prometheus setup |
| IoT Core | High | Medium-High | High | Real-time | On-premises, edge computing |

### Recommended Approach

**For most use cases**: Lambda + Redfish API
- Serverless (no infrastructure management)
- Cost-effective for moderate metric volumes
- Easy to scale across multiple servers
- Native AWS integration
- Modern API (JSON-based)

**For existing SNMP infrastructure**: EC2 + SNMP
- Leverage existing SNMP knowledge
- Compatible with legacy monitoring tools
- Lower learning curve

### Use Cases

- Real-time hardware monitoring
- Predictive maintenance
- Performance optimization
- Capacity planning
- Energy efficiency analysis
- Compliance and reporting

## Best Practices

1. **License Verification**: Ensure iDRAC Datacenter license is active
2. **Platform Compatibility**: Verify server generation (14G or newer)
3. **API Documentation**: Reference platform-specific Telemetry Guide
4. **Metric Selection**: Choose relevant metrics based on monitoring goals
5. **Polling Intervals**: Configure appropriate sensing intervals to balance granularity and overhead

## Additional Resources

- Dell Support website for platform-specific documentation
- Dell GitHub repositories for reference implementations
- Redfish API specification for standard compliance
- iDRAC user guides for configuration details

---

*Report generated: December 8, 2025*
