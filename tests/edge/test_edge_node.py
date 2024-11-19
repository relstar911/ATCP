import pytest
import asyncio
from src.edge.edge_node import EdgeNode, NodeConfig

@pytest.fixture
def valid_config():
    return NodeConfig(
        node_id="test_node_1",
        cpu_cores=4,
        ram_gb=16,
        storage_gb=256,
        network_bandwidth_mbps=100
    )

@pytest.fixture
def invalid_config():
    return NodeConfig(
        node_id="test_node_2",
        cpu_cores=2,  # Below minimum
        ram_gb=8,     # Below minimum
        storage_gb=128, # Below minimum
        network_bandwidth_mbps=50  # Below minimum
    )

@pytest.mark.asyncio
async def test_edge_node_initialization(valid_config):
    node = EdgeNode(valid_config)
    success = await node.initialize()
    assert success == True
    assert node.status == "ready"

@pytest.mark.asyncio
async def test_edge_node_initialization_with_invalid_config(invalid_config):
    node = EdgeNode(invalid_config)
    success = await node.initialize()
    assert success == False
    assert node.status == "failed" 