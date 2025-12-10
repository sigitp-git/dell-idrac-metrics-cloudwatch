# Dell iDRAC Fleet Emulator

Extended version of the Dell iDRAC emulator that simulates metrics for 200 Dell servers publishing to AWS CloudWatch.

## Features

- **200 Server Emulation**: Simulates a fleet of 200 Dell servers with unique IDs
- **Realistic Metrics**: Each server generates independent thermal, power, and performance metrics
- **CloudWatch Integration**: Publishes all metrics to AWS CloudWatch namespace `Dell/iDRAC/Fleet`
- **Efficient Batching**: Optimized CloudWatch API usage with batch publishing
- **Monitoring Tools**: Built-in monitoring and status checking

## Quick Start

### 1. Start the Fleet Emulator

```bash
python start_fleet_emulator.py
```

This will:
- Check AWS credentials
- Start emulating 200 servers (DELL-SRV-001 through DELL-SRV-200)
- Publish metrics every 60 seconds to CloudWatch

### 2. Monitor Metrics (Optional)

In another terminal:
```bash
python monitor_fleet_metrics.py
```

This will show real-time statistics from CloudWatch.

## Server Configuration

Each emulated server generates these metrics:

- **Thermal**: CPU1/CPU2 temperatures, inlet/exhaust temperatures, disk temperature
- **Cooling**: Fan1/Fan2 speeds
- **Power**: Power consumption
- **Performance**: CPU usage, memory usage

## CloudWatch Metrics

All metrics are published to the `Dell/iDRAC/Fleet` namespace with dimensions:
- `ServerID`: Unique server identifier (DELL-SRV-001 to DELL-SRV-200)
- `MetricType`: Thermal, Cooling, Power, Performance, or General

### Example Metrics:
- `cpu1_temp` - CPU 1 temperature
- `power_consumption` - Power consumption in watts
- `fan1_speed` - Fan 1 speed in RPM
- `cpu_usage` - CPU utilization percentage
- `memory_usage` - Memory utilization percentage

## Scaling Configuration

To change the number of servers, edit `multi_server_emulator.py`:

```python
NUM_SERVERS = 200  # Change this value
PUBLISH_INTERVAL = 60  # Publishing interval in seconds
```

## AWS Costs

With 200 servers × 10 metrics × 1440 minutes/day = ~2.88M metric data points per day.

Estimated CloudWatch costs:
- Custom metrics: ~$2,880/month (at $1/metric/month for first 10K metrics)
- API requests: Minimal additional cost

## Files

- `multi_server_emulator.py` - Main fleet emulator
- `start_fleet_emulator.py` - Startup script with credential checking
- `monitor_fleet_metrics.py` - Real-time metrics monitoring
- `README_FLEET.md` - This documentation

## Stopping the Emulator

Press `Ctrl+C` in the terminal running the emulator to stop it gracefully.

## Troubleshooting

### No metrics in CloudWatch
1. Check AWS credentials: `aws sts get-caller-identity`
2. Verify CloudWatch permissions
3. Check emulator logs for errors

### High AWS costs
1. Reduce `NUM_SERVERS` in the script
2. Increase `PUBLISH_INTERVAL` to reduce frequency
3. Monitor CloudWatch usage in AWS console
