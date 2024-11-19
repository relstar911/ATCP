from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

@dataclass
class NodeConfig:
    node_id: str
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    network_bandwidth_mbps: int

class EdgeNode:
    def __init__(self, config: NodeConfig):
        self.config = config
        self.status = "initialized"
        self.last_heartbeat = None
        self.metrics = {}
        self.logger = logging.getLogger(f"edge_node_{config.node_id}")
        
    async def initialize(self) -> bool:
        """Initialize the edge node and verify system requirements"""
        try:
            self._setup_logging()
            await self._verify_system_requirements()
            self.status = "ready"
            self.last_heartbeat = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            self.status = "failed"
            return False

    async def _verify_system_requirements(self) -> bool:
        """Verify that the system meets minimum requirements"""
        min_requirements = {
            "cpu_cores": 4,
            "ram_gb": 16,
            "storage_gb": 256,
            "network_bandwidth_mbps": 100
        }
        
        if (self.config.cpu_cores < min_requirements["cpu_cores"] or
            self.config.ram_gb < min_requirements["ram_gb"] or
            self.config.storage_gb < min_requirements["storage_gb"] or
            self.config.network_bandwidth_mbps < min_requirements["network_bandwidth_mbps"]):
            raise ValueError("System does not meet minimum requirements")
        return True

    def _setup_logging(self) -> None:
        """Configure logging for the edge node"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ) 