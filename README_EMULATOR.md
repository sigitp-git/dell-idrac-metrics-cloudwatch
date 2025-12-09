# Dell iDRAC Metrics Emulator

A comprehensive Python-based emulator for Dell iDRAC that provides Redfish API, SNMP endpoints, and AWS CloudWatch integration for testing and development purposes.

## Features

- **Redfish API Server**: Full REST API emulating Dell iDRAC Redfish endpoints
- **SNMP Agent**: SNMP v1/v2c/v3 support with Dell MIB OIDs
- **CloudWatch Integration**: Automatic metric publishing to AWS CloudWatch
- **Realistic Metrics**: Simulated thermal, power, fan, and system metrics
- **Authentication**: HTTP Basic Auth for Redfish, community strings for SNMP

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Dell iDRAC Emulator                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Redfish    │  │     SNMP     │  │   CloudWatch    │  │
│  │   API Server │  │     Agent    │  │    Publisher    │  │
│  │  (Port 5000) │  │  (Port 1161) │  │  (Background)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│         │                 │                    │           │
│         └─────────────────┴────────────────────┘           │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │ Metrics         │                       │
│                  │ Generator       │                       │
│                  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS CLI configured with credentials (for CloudWatch)
- net-snmp tools (for SNMP testing)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### AWS Configuration

Configure AWS credentials for CloudWatch integration:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Usage

### 1. Start Redfish API Server

```bash
python idrac_emulator.py
```

The server will start on `http://0.0.0.0:5000` with:
- Default username: `root`
- Default password: `calvin`

### 2. Start SNMP Agent (Optional)

In a separate terminal:

```bash
python snmp_agent.py
```

The SNMP agent will start on port `1161` (non-privileged port) with:
- Community string (read): `public`
- Community string (write): `private`
- SNMPv3 user: `idrac-user` / `authkey123` / `privkey123`

### 3. Run Tests

```bash
python test_emulator.py
```

## API Endpoints

### Redfish API

| Endpoint | Description |
|----------|-------------|
| `/redfish/v1` | Service root |
| `/redfish/v1/Chassis` | Chassis collection |
| `/redfish/v1/Chassis/System.Embedded.1/Thermal` | Thermal metrics (temps, fans) |
| `/redfish/v1/Chassis/System.Embedded.1/Power` | Power metrics |
| `/redfish/v1/TelemetryService/MetricDefinitions` | Metric definitions |
| `/status` | Emulator status (no auth required) |

### Example Redfish Requests

```bash
# Get service root
curl -u root:calvin http://localhost:5000/redfish/v1

# Get thermal metrics
curl -u root:calvin http://localhost:5000/redfish/v1/Chassis/System.Embedded.1/Thermal

# Get power metrics
curl -u root:calvin http://localhost:5000/redfish/v1/Chassis/System.Embedded.1/Power

# Get status (no auth)
curl http://localhost:5000/status
```

### SNMP OIDs

Dell Enterprise OID Base: `1.3.6.1.4.1.674`

| Metric | OID |
|--------|-----|
| CPU Temperature | `1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1.0` |
| Inlet Temperature | `1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.2.0` |
| Exhaust Temperature | `1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.3.0` |
| Fan1 Speed | `1.3.6.1.4.1.674.10892.5.4.700.12.1.6.1.1.0` |
| Fan2 Speed | `1.3.6.1.4.1.674.10892.5.4.700.12.1.6.1.2.0` |
| Fan3 Speed | `1.3.6.1.4.1.674.10892.5.4.700.12.1.6.1.3.0` |
| Power Consumption | `1.3.6.1.4.1.674.10892.5.4.600.30.1.6.1.3.0` |
| System Status | `1.3.6.1.4.1.674.10892.5.4.200.10.1.4.1.0` |

### Example SNMP Requests

```bash
# Get CPU temperature
snmpget -v2c -c public localhost:1161 1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1.0

# Get power consumption
snmpget -v2c -c public localhost:1161 1.3.6.1.4.1.674.10892.5.4.600.30.1.6.1.3.0

# Walk all Dell OIDs
snmpwalk -v2c -c public localhost:1161 1.3.6.1.4.1.674

# SNMPv3 query
snmpget -v3 -l authPriv -u idrac-user -a MD5 -A authkey123 \
  -x DES -X privkey123 localhost:1161 1.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1.0
```

## CloudWatch Integration

### Automatic Publishing

Metrics are automatically published to CloudWatch every 60 seconds in the namespace `Dell/iDRAC/Emulated`.

### Published Metrics

- `CPU1_Temperature` (Thermal)
- `CPU2_Temperature` (Thermal)
- `Inlet_Temperature` (Thermal)
- `Exhaust_Temperature` (Thermal)
- `Fan1_Speed` (Thermal)
- `Fan2_Speed` (Thermal)
- `Fan3_Speed` (Thermal)
- `Power_Consumption` (Power)
- `CPU_Usage` (Performance)
- `Memory_Usage` (Performance)

### Dimensions

Each metric includes:
- `ServerID`: `emulated-server-001`
- `MetricType`: `Thermal`, `Power`, or `Performance`

### View CloudWatch Metrics

```bash
# List all metrics
aws cloudwatch list-metrics --namespace Dell/iDRAC/Emulated

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace Dell/iDRAC/Emulated \
  --metric-name CPU1_Temperature \
  --dimensions Name=ServerID,Value=emulated-server-001 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Average
```

## Simulated Metrics

The emulator generates realistic metrics with random variations:

| Metric | Range | Unit |
|--------|-------|------|
| CPU Temperature | 40-85°C | Celsius |
| Memory Temperature | 35-65°C | Celsius |
| Inlet Temperature | 20-35°C | Celsius |
| Exhaust Temperature | 30-50°C | Celsius |
| Fan Speed | 2000-8000 | RPM |
| Power Consumption | 200-600 | Watts |
| CPU Usage | 10-85 | Percent |
| Memory Usage | 30-75 | Percent |

## Configuration

### Customize Server ID

Edit `idrac_emulator.py`:

```python
SERVER_ID = "your-server-id"
```

### Customize CloudWatch Namespace

Edit `idrac_emulator.py`:

```python
CLOUDWATCH_NAMESPACE = "Your/Custom/Namespace"
```

### Change Publishing Interval

Edit the `cloudwatch_publisher_loop()` function:

```python
time.sleep(60)  # Change to desired interval in seconds
```

### Disable CloudWatch Publishing

Edit `idrac_emulator.py`:

```python
cw_publisher.enabled = False
```

## Troubleshooting

### Port 161 Permission Denied

SNMP typically uses port 161, which requires root privileges. The emulator uses port 1161 by default.

To use port 161:

```bash
sudo python snmp_agent.py
```

Or modify `snmp_agent.py`:

```python
agent = DellSNMPAgent(host='0.0.0.0', port=161)
```

### CloudWatch Access Denied

Ensure your AWS credentials have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

### SNMP Tools Not Found

Install net-snmp tools:

**Ubuntu/Debian:**
```bash
sudo apt-get install snmp snmp-mibs-downloader
```

**RHEL/CentOS:**
```bash
sudo yum install net-snmp net-snmp-utils
```

**macOS:**
```bash
brew install net-snmp
```

## Development

### Adding New Metrics

1. Add metric generation in `MetricsGenerator` class
2. Add Redfish endpoint in `idrac_emulator.py`
3. Add SNMP OID in `snmp_agent.py`
4. Add CloudWatch metric in `CloudWatchPublisher.collect_and_publish()`

### Example: Adding GPU Temperature

```python
# In MetricsGenerator
def get_gpu_temperature(self, gpu_id=1):
    return round(random.uniform(40, 90), 1)

# In Redfish thermal endpoint
{
    "Name": "GPU1 Temp",
    "ReadingCelsius": metrics_gen.get_gpu_temperature(1)
}

# In SNMP agent
GPU_TEMP_OID = DELL_OID_BASE + (10892, 5, 4, 700, 20, 1, 6, 1, 10)

# In CloudWatch publisher
{
    'name': 'GPU1_Temperature',
    'value': metrics_gen.get_gpu_temperature(1),
    'type': 'Thermal'
}
```

## Use Cases

- **Testing monitoring systems** without physical hardware
- **Developing CloudWatch integrations** for Dell servers
- **Training and demonstrations** of iDRAC capabilities
- **CI/CD pipeline testing** for infrastructure monitoring
- **Load testing** monitoring dashboards
- **Prototyping** custom monitoring solutions

## Limitations

- Simulated metrics only (not real hardware data)
- Limited MIB implementation (core metrics only)
- No SNMP trap generation
- No Redfish event subscriptions
- No persistent storage of metrics

## License

This is an educational/testing tool. Not affiliated with Dell Technologies.

## References

- [Dell iDRAC Telemetry Reference Guide](https://www.dell.com/support)
- [Redfish API Specification](https://www.dmtf.org/standards/redfish)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Net-SNMP Documentation](http://www.net-snmp.org/)
