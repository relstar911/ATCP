import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json
from src.network.p2p.node import P2PNode, NodeStatus

@pytest.fixture
async def mock_connection():
    """Einfacher Connection-Mock"""
    reader = AsyncMock()
    writer = AsyncMock()
    
    handshake_data = {
        "node_id": "test_peer",
        "capabilities": {
            "version": "1.0.0",
            "features": ["data_sharing"]
        }
    }
    
    async def mock_read(*args):
        return json.dumps(handshake_data).encode()
    
    reader.read = AsyncMock(side_effect=mock_read)
    writer.get_extra_info.return_value = ('127.0.0.1', 8002)
    writer.drain = AsyncMock()
    writer.close = AsyncMock()
    writer.wait_closed = AsyncMock()
    
    return reader, writer

@pytest.mark.asyncio
async def test_peer_connection_mock(mock_connection):
    """Basis-Test für Peer-Verbindung"""
    reader, writer = mock_connection
    
    async def mock_open_connection(*args, **kwargs):
        return reader, writer
    
    node1 = P2PNode("localhost", 8001)
    node2 = P2PNode("localhost", 8002)
    
    try:
        with patch('asyncio.open_connection', new=mock_open_connection):
            await node1.start()
            success = await node2.connect_to_peer("localhost", 8001)
            
            assert success
            assert len(node2.peers) == 1
            
            peer = next(iter(node2.peers.values()))
            assert peer.status == NodeStatus.READY
    finally:
        await node1.stop()
        await node2.stop()

@pytest.mark.asyncio
async def test_handshake(mock_connection):
    """Basis-Test für Handshake"""
    reader, writer = mock_connection
    
    async def mock_open_connection(*args, **kwargs):
        return reader, writer
    
    node1 = P2PNode("localhost", 8001)
    node2 = P2PNode("localhost", 8002)
    
    try:
        with patch('asyncio.open_connection', new=mock_open_connection):
            await node1.start()
            success = await node2.connect_to_peer("localhost", 8001)
            
            assert success
            peer = next(iter(node2.peers.values()))
            assert peer.node_id == "test_peer"
            assert peer.capabilities["version"] == "1.0.0"
    finally:
        await node1.stop()
        await node2.stop()