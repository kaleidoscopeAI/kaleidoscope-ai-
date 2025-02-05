import psutil
import time

class PerformanceTracker:
    def __init__(self, node_manager: NodeLifeCycleManager):
        self.node_manager = node_manager
        self.performance_data = {}
        self.last_update = time.time()

    def collect_performance_data(self):
        """Collect performance metrics for each node."""
        current_time = time.time()
        for node_id, node in self.node_manager.nodes.items():
            try:
                # CPU usage
                cpu_usage = psutil.cpu_percent(interval=1, percpu=True)

                # RAM usage
                ram = psutil.virtual_memory()
                ram_usage = ram.percent
                ram_total = ram.total
                ram_available = ram.available

                # Disk usage
                disk = psutil.disk_usage('/')  # Assuming root partition
                disk_usage = disk.percent
                disk_total = disk.total
                disk_free = disk.free

                # Network usage
                net_io_counters = psutil.net_io_counters()
                bytes_sent = net_io_counters.bytes_sent
                bytes_recv = net_io_counters.bytes_recv

                # Update performance data
                self.performance_data[node_id] = {
                    'timestamp': current_time,
                    'cpu_usage': cpu_usage,
                    'ram_usage': ram_usage,
                    'ram_total': ram_total,
                    'ram_available': ram_available,
                    'disk_usage': disk_usage,
                    'disk_total': disk_total,
                    'disk_free': disk_free,
                    'bytes_sent': bytes_sent,
                    'bytes_recv': bytes_recv
                }

            except Exception as e:
                print(f"Error collecting performance data for node {node_id}: {e}")

        self.last_update = current_time

    def get_performance_data(self, node_id: str = None) -> dict:
        """Get the latest performance data, optionally for a specific node."""
        if node_id:
            return self.performance_data.get(node_id, {})
        else:
            return self.performance_data

    def get_historical_performance_data(self, node_id: str, time_range: int = 3600) -> list:
        """Get historical performance data for a node within a specific time range."""
        historical_data = []
        current_time = time.time()
        for data_point in reversed(self.performance_data.get(node_id, [])):
            if current_time - data_point['timestamp'] <= time_range:
                historical_data.append(data_point)
            else:
                break
        return historical_data
    
    def get_state(self) -> dict:
      """Return the current state of the performance tracker."""
      return {
          'last_update': self.last_update,
          'performance_data': self.performance_data
      }
