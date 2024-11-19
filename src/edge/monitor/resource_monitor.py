import psutil
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ResourceMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    timestamp: datetime

class ResourceMonitor:
    def __init__(self, interval_seconds: int = 5):
        self.interval = interval_seconds
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.last_metrics: Optional[ResourceMetrics] = None
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0
        }

    async def start_monitoring(self):
        """Startet das kontinuierliche Monitoring der Systemressourcen."""
        self.is_monitoring = True
        try:
            while self.is_monitoring:
                metrics = await self.get_current_metrics()
                await self._check_thresholds(metrics)
                self.last_metrics = metrics
                await asyncio.sleep(self.interval)
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}", exc_info=True)
            self.is_monitoring = False
            raise

    async def stop_monitoring(self):
        """Stoppt das Ressourcen-Monitoring."""
        self.is_monitoring = False

    async def get_current_metrics(self) -> ResourceMetrics:
        """Erfasst aktuelle Systemressourcen."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()._asdict()

            return ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io={
                    'bytes_sent': network['bytes_sent'],
                    'bytes_recv': network['bytes_recv']
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}", exc_info=True)
            raise

    async def _check_thresholds(self, metrics: ResourceMetrics) -> None:
        """Überprüft, ob Ressourcennutzung Schwellenwerte überschreitet."""
        warnings = []

        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            warnings.append(f"CPU usage critical: {metrics.cpu_percent}%")
            
        if metrics.memory_percent > self.thresholds['memory_percent']:
            warnings.append(f"Memory usage critical: {metrics.memory_percent}%")
            
        if metrics.disk_usage_percent > self.thresholds['disk_usage_percent']:
            warnings.append(f"Disk usage critical: {metrics.disk_usage_percent}%")

        if warnings:
            self.logger.warning("Resource warnings: " + "; ".join(warnings))

    def get_status(self) -> Dict[str, Any]:
        """Liefert den aktuellen Monitoring-Status."""
        return {
            "is_monitoring": self.is_monitoring,
            "last_metrics": self.last_metrics.__dict__ if self.last_metrics else None,
            "thresholds": self.thresholds
        } 