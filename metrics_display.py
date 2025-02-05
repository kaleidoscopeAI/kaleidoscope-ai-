system_monitoring/visualization/metrics_display.py
Python

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from collections import deque

class MetricsDisplay:
    def __init__(self, performance_tracker: PerformanceTracker, update_interval: int = 5000):
        self.performance_tracker = performance_tracker
        self.update_interval = update_interval  # in milliseconds
        self.fig, self.axs = plt.subplots(2, 2, figsize=(12, 8))  # Adjust for desired metrics
        self.data_buffers = {}

        # Initialize data buffers for each metric
        for node_id in self.performance_tracker.node_manager.nodes.keys():
            self.data_buffers[node_id] = {
                'timestamps': deque(maxlen=60),  # Store data for the last 60 intervals
                'cpu_usage': deque(maxlen=60),
                'ram_usage': deque(maxlen=60),
                'disk_usage': deque(maxlen=60),
                'network_sent': deque(maxlen=60),
                'network_recv': deque(maxlen=60)
            }

        self.setup_plots()

    def setup_plots(self):
      """Set up the initial plots."""
      metrics = ['cpu_usage', 'ram_usage', 'disk_usage', 'network_sent']
      colors = ['r', 'g', 'b', 'y']  # Colors for different metrics
  
      for ax, metric, color in zip(self.axs.flat, metrics, colors):
          ax.set_title(metric.upper())
          ax.set_xlabel('Time (s)')
          ax.set_ylabel('%' if metric != 'network_sent' else 'Bytes')
          ax.set_ylim(0, 100 if metric != 'network_sent' else 0, 50000)  # Initial y-axis limit for network_sent
  
          # Create a line for each node
          for node_id in self.performance_tracker.node_manager.nodes.keys():
              line, = ax.plot([], [], '-', label=f'{node_id}', color=color, alpha=0.7) # added color and transparency for each node
              
              # Store the line objects for updating later
              if 'lines' not in self.data_buffers[node_id]:
                  self.data_buffers[node_id]['lines'] = {}
              self.data_buffers[node_id]['lines'][metric] = line
  
          ax.legend()
          ax.grid(True)
  
      plt.tight_layout()
  
    def update_data(self):
        """Update data buffers with the latest performance data."""
        self.performance_tracker.collect_performance_data()
        current_time = time.time()

        for node_id, performance_data in self.performance_tracker.performance_data.items():
            if node_id in self.data_buffers:
                self.data_buffers[node_id]['timestamps'].append(current_time)
                self.data_buffers[node_id]['cpu_usage'].append(np.mean(performance_data['cpu_usage']))
                self.data_buffers[node_id]['ram_usage'].append(performance_data['ram_usage'])
                self.data_buffers[node_id]['disk_usage'].append(performance_data['disk_usage'])
                
                # Calculate network sent/received rate
                if len(self.data_buffers[node_id]['network_sent']) > 0:
                    time_diff = current_time - self.data_buffers[node_id]['timestamps'][-2]
                    sent_diff = performance_data['bytes_sent'] - self.data_buffers[node_id]['network_sent'][-1]
                    recv_diff = performance_data['bytes_recv'] - self.data_buffers[node_id]['network_recv'][-1]
                    self.data_buffers[node_id]['network_sent'].append(sent_diff / time_diff if time_diff > 0 else 0)
                    self.data_buffers[node_id]['network_recv'].append(recv_diff / time_diff if time_diff > 0 else 0)
                else:
                    self.data_buffers[node_id]['network_sent'].append(0)
                    self.data_buffers[node_id]['network_recv'].append(0)

    def update_plots(self, i):
        """Update the plots with the latest data."""
        self.update_data()

        for ax, metric in zip(self.axs.flat, ['cpu_usage', 'ram_usage', 'disk_usage', 'network_sent']):
            for node_id in self.performance_tracker.node_manager.nodes.keys():
                if node_id in self.data_buffers and metric in self.data_buffers[node_id]:
                    x_data = list(self.data_buffers[node_id]['timestamps'])
                    y_data = list(self.data_buffers[node_id][metric])

                    # Update line data
                    self.data_buffers[node_id]['lines'][metric].set_data(x_data, y_data)

                    # Rescale the axes if needed
                    if y_data:
                        ax.set_xlim(min(x_data), max(x_data))
                        if metric != 'network_sent':
                            ax.set_ylim(0, max(100, max(y_data) * 1.1))
                        else:
                            ax.set_ylim(0, max(y_data) * 1.1)  # Adjust for network_sent

        return [line for node_data in self.data_buffers.values() for line in node_data['lines'].values()]

    def animate(self):
      """Start the animation."""
      ani = animation.FuncAnimation(
          self.fig,
          self.update_plots,
          interval=self.update_interval,
          blit=False  # Changed blit to False
      )
      plt.show()

    def get_state(self) -> dict:
        """Returns the current state of the metrics display."""
        return {
            'update_interval': self.update_interval,
            'data_buffers': {node_id: {metric: list(data) for metric, data in node_data.items() if metric != 'lines'} for node_id, node_data in self.data_buffers.items()}
        }
