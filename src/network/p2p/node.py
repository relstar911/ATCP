from dataclasses import dataclass
from typing import Dict, Set, Optional, Any, Callable, Awaitable
import asyncio
import logging
from enum import Enum
import uuid
import json
import time

class NodeStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class PeerInfo:
    node_id: str
    address: str
    port: int
    status: NodeStatus
    last_seen: float
    capabilities: Dict[str, Any]

class P2PNode:
    def __init__(self, host: str, port: int, node_id: Optional[str] = None):
        self.host = host
        self.port = port
        self.node_id = node_id or str(uuid.uuid4())
        self.peers: Dict[str, PeerInfo] = {}
        self.status = NodeStatus.INITIALIZING
        self.logger = logging.getLogger(__name__)
        self.message_handlers: Dict[str, Callable[[Dict[str, Any], PeerInfo], Awaitable[None]]] = {}
        self.server: Optional[asyncio.Server] = None

    def _generate_node_id(self) -> str:
        """Generiert eine eindeutige Node-ID."""
        return str(uuid.uuid4())

    async def start(self):
        """Startet den P2P-Node und initialisiert die Netzwerkkommunikation."""
        try:
            self.server = await asyncio.start_server(
                self._handle_connection, self.host, self.port
            )
            
            self.status = NodeStatus.READY
            self.logger.info(f"P2P Node {self.node_id} listening on {self.host}:{self.port}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            self.status = NodeStatus.ERROR
            self.logger.error(f"Failed to start P2P node: {str(e)}")
            raise

    async def stop(self):
        """Stoppt den P2P-Node und schließt alle Verbindungen."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.status = NodeStatus.DISCONNECTED
            self.logger.info(f"P2P Node {self.node_id} stopped")

    async def connect_to_peer(self, address: str, port: int) -> bool:
        """Verbindet sich mit einem Peer."""
        try:
            self.status = NodeStatus.CONNECTING
            reader, writer = await asyncio.open_connection(address, port)
            
            # Handshake durchführen
            peer_info = await self._perform_handshake(reader, writer)
            if peer_info:
                self.peers[peer_info.node_id] = peer_info
                self.status = NodeStatus.READY
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to peer {address}:{port}: {str(e)}")
            self.status = NodeStatus.ERROR
            return False

    async def _perform_handshake(self, 
                                reader: asyncio.StreamReader, 
                                writer: asyncio.StreamWriter) -> Optional[PeerInfo]:
        """Führt den Handshake mit einem Peer durch."""
        try:
            # Sende unsere Node-Info
            handshake_data = {
                "node_id": self.node_id,
                "capabilities": {
                    "version": "1.0.0",
                    "features": ["data_sharing"]
                }
            }
            writer.write(json.dumps(handshake_data).encode())
            await writer.drain()
            
            # Empfange Peer-Info
            data = await reader.read(1024)
            if not data:
                return None
            
            peer_data = json.loads(data.decode())
            return PeerInfo(
                node_id=peer_data["node_id"],
                address=writer.get_extra_info('peername')[0],
                port=writer.get_extra_info('peername')[1],
                status=NodeStatus.READY,
                last_seen=time.time(),
                capabilities=peer_data["capabilities"]
            )
        except Exception as e:
            self.logger.error(f"Handshake failed: {str(e)}")
            return None

    def register_message_handler(self, 
                               message_type: str, 
                               handler: Callable[[Dict[str, Any], PeerInfo], Awaitable[None]]):
        """Registriert einen Handler für einen bestimmten Nachrichtentyp."""
        self.message_handlers[message_type] = handler

    async def broadcast_message(self, message: Dict[str, Any]):
        """Sendet eine Nachricht an alle verbundenen Peers."""
        for peer_id, peer in self.peers.items():
            try:
                # Implementierung des Nachrichtenversands
                pass
            except Exception as e:
                self.logger.error(f"Failed to send message to peer {peer_id}: {str(e)}")

    async def _handle_connection(self, reader: asyncio.StreamReader, 
                               writer: asyncio.StreamWriter):
        """Behandelt eingehende Verbindungen."""
        peer_address = writer.get_extra_info('peername')
        try:
            # Handshake durchführen
            peer_info = await self._perform_handshake(reader, writer)
            if peer_info:
                self.peers[peer_info.node_id] = peer_info
                self.logger.info(f"New peer connected: {peer_info.node_id}")
            
            # Verbindung verwalten
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                    
                message = json.loads(data.decode())
                if message.get('type') in self.message_handlers:
                    await self.message_handlers[message['type']](message, peer_info)
                
        except Exception as e:
            self.logger.error(f"Error handling connection from {peer_address}: {str(e)}")
        finally:
            if peer_info and peer_info.node_id in self.peers:
                del self.peers[peer_info.node_id]
            writer.close()
            await writer.wait_closed() 