import asyncio
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
from collections import deque
import websockets
import aioredis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class SystemState:
    """Tracks the current state of the Kaleidoscope system."""
    active_nodes: Dict[str, Dict] = field(default_factory=dict)
    task_queue: deque = field(default_factory=lambda: deque(maxlen=1000))
    insight_buffer: deque = field(default_factory=lambda: deque(maxlen=1000))
    total_energy: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    connected_clients: Set[websockets.WebSocketServerProtocol] = field(default_factory=set)

class RealtimeUpdateManager:
    """
    Manages real-time updates and state synchronization for the Kaleidoscope AI system.
    Provides WebSocket connections for live monitoring and state updates.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.state = SystemState()
        self.redis = None  # Will be initialized in start()
        self._running = False
        self._update_task = None

    async def start(self):
        """Initialize and start the update manager."""
        try:
            # Initialize Redis for state management
            self.redis = await aioredis.create_redis_pool(
                'redis://localhost',
                encoding='utf-8'
            )
            
            # Start WebSocket server
            server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port
            )
            
            self._running = True
            self._update_task = asyncio.create_task(self._periodic_updates())
            
            logging.info(f"RealtimeUpdate manager started on ws://{self.host}:{self.port}")
            
            # Keep the server running
            await server.wait_closed()
            
        except Exception as e:
            logging.error(f"Failed to start RealtimeUpdate manager: {str(e)}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the update manager and cleanup resources."""
        self._running = False
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        # Close all client connections
        for client in self.state.connected_clients:
            try:
                await client.close()
            except:
                pass
        
        # Cleanup Redis connection
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

        logging.info("RealtimeUpdate manager stopped")

    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new client connections and their messages."""
        try:
            # Register new client
            self.state.connected_clients.add(websocket)
            logging.info(f"New client connected. Total clients: {len(self.state.connected_clients)}")
            
            # Send initial state
            await self._send_state_update(websocket)
            
            # Handle client messages
            async for message in websocket:
                try:
                    await self._process_client_message(websocket, message)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Invalid JSON format"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client connection closed")
        finally:
            self.state.connected_clients.remove(websocket)

    async def _process_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Process incoming client messages."""
        data = json.loads(message)
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # Handle subscription requests
            topics = data.get('topics', [])
            await self._handle_subscription(websocket, topics)
            
        elif msg_type == 'query':
            # Handle state queries
            query = data.get('query', {})
            result = await self._handle_query(query)
            await websocket.send(json.dumps({
                'type': 'query_result',
                'data': result
            }))

    async def _handle_subscription(self, websocket: websockets.WebSocketServerProtocol, topics: List[str]):
        """Handle client subscription to specific update topics."""
        # Store subscription preferences in Redis
        await self.redis.hset(
            f"client:{id(websocket)}",
            'topics',
            json.dumps(topics)
        )
        
        await websocket.send(json.dumps({
            'type': 'subscription_confirmed',
            'topics': topics
        }))

    async def _handle_query(self, query: Dict) -> Dict:
        """Handle specific state queries from clients."""
        result = {}
        
        if 'nodes' in query:
            result['nodes'] = self.state.active_nodes
            
        if 'tasks' in query:
            result['tasks'] = list(self.state.task_queue)
            
        if 'insights' in query:
            result['insights'] = list(self.state.insight_buffer)
            
        if 'energy' in query:
            result['total_energy'] = self.state.total_energy
            
        return result

    async def _periodic_updates(self):
        """Periodically send updates to all connected clients."""
        while self._running:
            try:
                await self._update_system_state()
                await self._broadcast_state_update()
                await asyncio.sleep(1.0)  # Update frequency
                
            except Exception as e:
                logging.error(f"Error in periodic update: {str(e)}")
                await asyncio.sleep(5.0)  # Backup sleep on error

    async def _update_system_state(self):
        """Update the internal system state."""
        # Update node states
        nodes_data = await self.redis.hgetall('nodes')
        self.state.active_nodes = {
            node_id: json.loads(data)
            for node_id, data in nodes_data.items()
        }
        
        # Update total energy
        self.state.total_energy = sum(
            node['energy'] for node in self.state.active_nodes.values()
        )
        
        self.state.last_update = datetime.now()

    async def _broadcast_state_update(self):
        """Broadcast state updates to all connected clients."""
        if not self.state.connected_clients:
            return
            
        update = {
            'type': 'state_update',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'nodes_count': len(self.state.active_nodes),
                'total_energy': self.state.total_energy,
                'tasks_pending': len(self.state.task_queue),
                'insights_count': len(self.state.insight_buffer)
            }
        }
        
        message = json.dumps(update)
        
        # Broadcast to all clients
        for client in self.state.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                continue

    async def _send_state_update(self, websocket: websockets.WebSocketServerProtocol):
        """Send current state to a specific client."""
        update = {
            'type': 'full_state',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'nodes': self.state.active_nodes,
                'tasks': list(self.state.task_queue),
                'insights': list(self.state.insight_buffer),
                'total_energy': self.state.total_energy
            }
        }
        
        await websocket.send(json.dumps(update))

    async def update_node_state(self, node_id: str, state: Dict):
        """Update the state of a specific node."""
        self.state.active_nodes[node_id] = state
        await self.redis.hset('nodes', node_id, json.dumps(state))
        
        # Broadcast update to relevant clients
        await self._broadcast_state_update()

    async def add_task(self, task: Dict):
        """Add a new task to the queue."""
        self.state.task_queue.append(task)
        await self._broadcast_state_update()

    async def add_insight(self, insight: Dict):
        """Add a new insight to the buffer."""
        self.state.insight_buffer.append(insight)
        await self._broadcast_state_update()

async def main():
    """Main entry point for the RealtimeUpdate manager."""
    manager = RealtimeUpdateManager()
    try:
        await manager.start()
    except KeyboardInterrupt:
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
