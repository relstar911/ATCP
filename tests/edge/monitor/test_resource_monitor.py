import pytest
from src.edge.monitor.resource_monitor import ResourceMonitor, ResourceMetrics
import asyncio

@pytest.fixture
def monitor():
    return ResourceMonitor(interval_seconds=1)

@pytest.mark.asyncio
async def test_get_current_metrics(monitor):
    metrics = await monitor.get_current_metrics()
    
    assert isinstance(metrics, ResourceMetrics)
    assert 0 <= metrics.cpu_percent <= 100
    assert 0 <= metrics.memory_percent <= 100
    assert 0 <= metrics.disk_usage_percent <= 100
    assert isinstance(metrics.network_io, dict)
    assert 'bytes_sent' in metrics.network_io
    assert 'bytes_recv' in metrics.network_io

@pytest.mark.asyncio
async def test_monitoring_cycle(monitor):
    # Starte Monitoring im Hintergrund
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    
    # Warte kurz, damit Monitoring starten kann
    await asyncio.sleep(2)
    
    # Prüfe Status
    status = monitor.get_status()
    assert status["is_monitoring"] == True
    assert status["last_metrics"] is not None
    
    # Stoppe Monitoring
    await monitor.stop_monitoring()
    await monitoring_task

@pytest.mark.asyncio
async def test_threshold_warnings(monitor):
    # Setze Schwellenwerte sehr niedrig für den Test
    monitor.thresholds = {
        'cpu_percent': 0.0,
        'memory_percent': 0.0,
        'disk_usage_percent': 0.0
    }
    
    metrics = await monitor.get_current_metrics()
    await monitor._check_thresholds(metrics)
    # Die Warnungen sollten in den Logs erscheinen

def test_initial_state(monitor):
    assert monitor.is_monitoring == False
    assert monitor.last_metrics is None
    assert isinstance(monitor.thresholds, dict) 

@pytest.mark.asyncio
async def test_monitoring_error_handling(monitor):
    # Simuliere einen Fehler während des Monitorings
    def raise_error():
        raise Exception("Simulated monitoring error")
    
    # Ersetze die get_current_metrics Methode temporär
    original_method = monitor.get_current_metrics
    monitor.get_current_metrics = raise_error
    
    with pytest.raises(Exception) as exc_info:
        await monitor.start_monitoring()
    
    assert str(exc_info.value) == "Simulated monitoring error"
    assert monitor.is_monitoring == False
    
    # Stelle die originale Methode wieder her
    monitor.get_current_metrics = original_method

@pytest.mark.asyncio
async def test_metrics_collection_error(monitor):
    # Simuliere einen Fehler bei der Metrik-Sammlung
    def raise_error():
        raise Exception("Metrics collection error")
    
    # Patch psutil.cpu_percent temporär
    import psutil
    original_cpu_percent = psutil.cpu_percent
    psutil.cpu_percent = raise_error
    
    with pytest.raises(Exception) as exc_info:
        await monitor.get_current_metrics()
    
    # Stelle original wieder her
    psutil.cpu_percent = original_cpu_percent