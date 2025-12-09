#!/usr/bin/env python3
"""
SNMP Agent for Dell iDRAC Emulator
Provides SNMP interface for metrics
"""

from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.proto.api import v2c
from pysnmp.smi import builder, view, compiler
import random
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DellSNMPAgent:
    """SNMP Agent emulating Dell iDRAC metrics"""
    
    # Dell Enterprise OID: 1.3.6.1.4.1.674
    DELL_OID_BASE = (1, 3, 6, 1, 4, 1, 674)
    
    # Dell Server Administrator MIB OIDs (10892.5.x.x)
    # Thermal OIDs
    CPU_TEMP_OID = DELL_OID_BASE + (10892, 5, 4, 700, 20, 1, 6, 1, 1)
    INLET_TEMP_OID = DELL_OID_BASE + (10892, 5, 4, 700, 20, 1, 6, 1, 2)
    EXHAUST_TEMP_OID = DELL_OID_BASE + (10892, 5, 4, 700, 20, 1, 6, 1, 3)
    
    # Fan OIDs
    FAN1_SPEED_OID = DELL_OID_BASE + (10892, 5, 4, 700, 12, 1, 6, 1, 1)
    FAN2_SPEED_OID = DELL_OID_BASE + (10892, 5, 4, 700, 12, 1, 6, 1, 2)
    FAN3_SPEED_OID = DELL_OID_BASE + (10892, 5, 4, 700, 12, 1, 6, 1, 3)
    
    # Power OIDs
    POWER_CONSUMPTION_OID = DELL_OID_BASE + (10892, 5, 4, 600, 30, 1, 6, 1, 3)
    POWER_STATUS_OID = DELL_OID_BASE + (10892, 5, 4, 600, 12, 1, 5, 1, 1)
    
    # System OIDs
    SYSTEM_STATUS_OID = DELL_OID_BASE + (10892, 5, 4, 200, 10, 1, 4, 1)
    CHASSIS_STATUS_OID = DELL_OID_BASE + (10892, 5, 4, 200, 10, 1, 4, 1)
    
    # Memory OIDs
    MEMORY_STATUS_OID = DELL_OID_BASE + (10892, 5, 4, 1100, 50, 1, 5, 1, 1)
    
    # Storage OIDs
    DISK_STATUS_OID = DELL_OID_BASE + (10892, 5, 5, 1, 20, 130, 4, 1, 4)
    
    def __init__(self, host='0.0.0.0', port=161):
        self.host = host
        self.port = port
        self.snmp_engine = engine.SnmpEngine()
        
    def generate_metrics(self):
        """Generate simulated metrics"""
        return {
            'cpu_temp': random.randint(40, 85),
            'inlet_temp': random.randint(20, 35),
            'exhaust_temp': random.randint(30, 50),
            'fan1_speed': random.randint(2000, 8000),
            'fan2_speed': random.randint(2000, 8000),
            'fan3_speed': random.randint(2000, 8000),
            'power_consumption': random.randint(200, 600),
            'power_status': 3,  # 3 = OK
            'system_status': 3,  # 3 = OK
            'chassis_status': 3,  # 3 = OK
            'memory_status': 3,  # 3 = OK
            'disk_status': 3  # 3 = OK
        }
    
    def setup_agent(self):
        """Setup SNMP agent configuration"""
        # Transport setup
        config.addTransport(
            self.snmp_engine,
            udp.domainName,
            udp.UdpTransport().openServerMode((self.host, self.port))
        )
        
        # SNMPv1/v2c setup
        config.addV1System(self.snmp_engine, 'public-read', 'public')
        config.addV1System(self.snmp_engine, 'private-write', 'private')
        
        # SNMPv3 setup
        config.addV3User(
            self.snmp_engine,
            'idrac-user',
            config.usmHMACMD5AuthProtocol, 'authkey123',
            config.usmDESPrivProtocol, 'privkey123'
        )
        
        # Allow full MIB access
        config.addVacmUser(
            self.snmp_engine, 1, 'public-read', 'noAuthNoPriv',
            (1, 3, 6, 1, 4, 1, 674), (1, 3, 6, 1, 4, 1, 674)
        )
        config.addVacmUser(
            self.snmp_engine, 2, 'public-read', 'noAuthNoPriv',
            (1, 3, 6, 1, 4, 1, 674), (1, 3, 6, 1, 4, 1, 674)
        )
        config.addVacmUser(
            self.snmp_engine, 3, 'idrac-user', 'authPriv',
            (1, 3, 6, 1, 4, 1, 674), (1, 3, 6, 1, 4, 1, 674)
        )
        
        # Create SNMP context
        snmp_context = context.SnmpContext(self.snmp_engine)
        
        # Register SNMP applications
        cmdrsp.GetCommandResponder(self.snmp_engine, snmp_context)
        cmdrsp.SetCommandResponder(self.snmp_engine, snmp_context)
        cmdrsp.NextCommandResponder(self.snmp_engine, snmp_context)
        cmdrsp.BulkCommandResponder(self.snmp_engine, snmp_context)
        
        # Add MIB objects
        self.add_mib_objects(snmp_context)
        
        logger.info(f"SNMP Agent configured on {self.host}:{self.port}")
        logger.info("Community strings: public (read), private (write)")
        logger.info("SNMPv3 user: idrac-user / authkey123 / privkey123")
    
    def add_mib_objects(self, snmp_context):
        """Add MIB objects to SNMP context"""
        mib_builder = snmp_context.getMibInstrum().getMibBuilder()
        mib_view = view.MibViewController(mib_builder)
        
        # Get current metrics
        metrics = self.generate_metrics()
        
        # Add scalar objects
        mib_instrum = snmp_context.getMibInstrum()
        
        # CPU Temperature
        mib_instrum.writeVars(
            ((self.CPU_TEMP_OID, 0), v2c.Integer(metrics['cpu_temp']))
        )
        
        # Inlet Temperature
        mib_instrum.writeVars(
            ((self.INLET_TEMP_OID, 0), v2c.Integer(metrics['inlet_temp']))
        )
        
        # Exhaust Temperature
        mib_instrum.writeVars(
            ((self.EXHAUST_TEMP_OID, 0), v2c.Integer(metrics['exhaust_temp']))
        )
        
        # Fan Speeds
        mib_instrum.writeVars(
            ((self.FAN1_SPEED_OID, 0), v2c.Integer(metrics['fan1_speed']))
        )
        mib_instrum.writeVars(
            ((self.FAN2_SPEED_OID, 0), v2c.Integer(metrics['fan2_speed']))
        )
        mib_instrum.writeVars(
            ((self.FAN3_SPEED_OID, 0), v2c.Integer(metrics['fan3_speed']))
        )
        
        # Power Consumption
        mib_instrum.writeVars(
            ((self.POWER_CONSUMPTION_OID, 0), v2c.Integer(metrics['power_consumption']))
        )
        
        # Status values
        mib_instrum.writeVars(
            ((self.POWER_STATUS_OID, 0), v2c.Integer(metrics['power_status']))
        )
        mib_instrum.writeVars(
            ((self.SYSTEM_STATUS_OID, 0), v2c.Integer(metrics['system_status']))
        )
        mib_instrum.writeVars(
            ((self.CHASSIS_STATUS_OID, 0), v2c.Integer(metrics['chassis_status']))
        )
        mib_instrum.writeVars(
            ((self.MEMORY_STATUS_OID, 0), v2c.Integer(metrics['memory_status']))
        )
        mib_instrum.writeVars(
            ((self.DISK_STATUS_OID, 0), v2c.Integer(metrics['disk_status']))
        )
        
        logger.info("MIB objects registered")
    
    def run(self):
        """Start SNMP agent"""
        self.setup_agent()
        logger.info("SNMP Agent started. Press Ctrl+C to stop.")
        
        try:
            self.snmp_engine.transportDispatcher.jobStarted(1)
            self.snmp_engine.transportDispatcher.runDispatcher()
        except KeyboardInterrupt:
            logger.info("SNMP Agent stopped by user")
        except Exception as e:
            logger.error(f"SNMP Agent error: {str(e)}")
        finally:
            self.snmp_engine.transportDispatcher.closeDispatcher()

if __name__ == '__main__':
    try:
        agent = DellSNMPAgent(host='0.0.0.0', port=1161)  # Using 1161 to avoid needing root
        logger.info("=" * 60)
        logger.info("Dell iDRAC SNMP Agent Emulator")
        logger.info("=" * 60)
        logger.info("Available OIDs:")
        logger.info(f"  CPU Temperature: {'.'.join(map(str, agent.CPU_TEMP_OID))}")
        logger.info(f"  Inlet Temperature: {'.'.join(map(str, agent.INLET_TEMP_OID))}")
        logger.info(f"  Fan1 Speed: {'.'.join(map(str, agent.FAN1_SPEED_OID))}")
        logger.info(f"  Power Consumption: {'.'.join(map(str, agent.POWER_CONSUMPTION_OID))}")
        logger.info("=" * 60)
        logger.info("Test with: snmpget -v2c -c public localhost:1161 <OID>")
        logger.info("=" * 60)
        agent.run()
    except PermissionError:
        logger.error("Permission denied. Try using port 1161 or run with sudo for port 161")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start SNMP agent: {str(e)}")
        sys.exit(1)
