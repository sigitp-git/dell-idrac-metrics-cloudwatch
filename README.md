# Dell iDRAC Metrics CloudWatch Integration

A Python-based emulator and monitoring solution for Dell iDRAC that provides Redfish API, SNMP endpoints, and AWS CloudWatch integration for testing and development purposes.

## Features

- **Redfish API Server**: Full REST API emulating Dell iDRAC Redfish endpoints
- **SNMP Agent**: SNMP v1/v2c/v3 support with Dell MIB OIDs
- **CloudWatch Integration**: Automatic metric publishing to AWS CloudWatch
- **Realistic Metrics**: Simulated thermal, power, fan, and system metrics
- **Authentication**: HTTP Basic Auth for Redfish, community strings for SNMP

## Quick Start

### Prerequisites

- Python 3.7+
- AWS credentials configured
- Required Python packages (see requirements.txt)

### Installation

```bash
git clone https://github.com/sigitp-git/dell-idrac-metrics-cloudwatch.git
cd dell-idrac-metrics-cloudwatch
pip install -r requirements.txt
```

### Usage

1. **Start the iDRAC Emulator**:
```bash
python idrac_emulator.py
```

2. **Start the SNMP Agent** (in another terminal):
```bash
python snmp_agent.py
```

3. **Run Tests**:
```bash
python test_emulator.py
```

## API Endpoints

### Redfish API (Port 5000)
- `GET /redfish/v1/` - Service root
- `GET /redfish/v1/Systems/System.Embedded.1` - System information
- `GET /redfish/v1/Chassis/System.Embedded.1/Thermal` - Thermal metrics
- `GET /redfish/v1/Chassis/System.Embedded.1/Power` - Power metrics

**Authentication**: Basic Auth (username: `root`, password: `calvin`)

### SNMP Agent (Port 161)
- Community string: `public`
- Supports Dell-specific OIDs for system monitoring

## CloudWatch Metrics

The emulator automatically publishes metrics to AWS CloudWatch under the namespace `Dell/iDRAC`:

- **Thermal**: CPU temperatures, inlet/exhaust temperatures
- **Power**: Power consumption, voltage readings
- **Fan**: Fan speeds and status
- **System**: Overall system health

## Configuration

### AWS Setup
Ensure your AWS credentials are configured:
```bash
aws configure
```

### Environment Variables
- `AWS_REGION`: AWS region for CloudWatch (default: us-east-1)
- `IDRAC_USERNAME`: Redfish API username (default: root)
- `IDRAC_PASSWORD`: Redfish API password (default: calvin)

## Project Structure

```
├── idrac_emulator.py      # Main Redfish API emulator
├── snmp_agent.py          # SNMP agent implementation
├── test_emulator.py       # Test suite
├── requirements.txt       # Python dependencies
├── README_EMULATOR.md     # Detailed emulator documentation
└── dell-idrac-metrics-research.md  # Research and implementation notes
```

## Testing

The project includes comprehensive tests for:
- Redfish API endpoints
- SNMP functionality
- CloudWatch integration
- Authentication mechanisms

Run all tests:
```bash
python test_emulator.py
```

## Documentation

- [Emulator Details](README_EMULATOR.md) - Comprehensive emulator documentation
- [Research Notes](dell-idrac-metrics-research.md) - Implementation research and notes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
