Python

import time
import json
import os

class DataStorage:
    def __init__(self, max_capacity: int = 10000, storage_directory: str = "data_storage"):
        self.data = []
        self.max_capacity = max_capacity
        self.storage_directory = storage_directory

        # Ensure storage directory exists
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def store_data(self, data_point: dict):
        """Store a data point with a timestamp."""
        timestamp = time.time()
        data_point_with_timestamp = {'timestamp': timestamp, 'data': data_point}
        self.data.append(data_point_with_timestamp)

        # Save to file (append mode)
        file_path = os.path.join(self.storage_directory, 'data.json')
        with open(file_path, 'a') as f:
            json.dump(data_point_with_timestamp, f)
            f.write('\n')  # Add a newline for each data point

        # Check capacity and remove oldest data if necessary
        if len(self.data) > self.max_capacity:
            self.data.pop(0)

    def retrieve_data(self, start_time, end_time) -> list:
        """Retrieve data within a specific time range."""
        retrieved_data = []
        for item in self.data:
            if start_time <= item['timestamp'] <= end_time:
                retrieved_data.append(item['data'])
        return retrieved_data

    def load_data_from_file(self, file_path: str = None):
        """Load data from a JSON file."""
        if file_path is None:
            file_path = os.path.join(self.storage_directory, 'data.json')
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        data_point = json.loads(line.strip())
                        self.data.append(data_point)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        # Maintain capacity after loading
        if len(self.data) > self.max_capacity:
            self.data = self.data[-self.max_capacity:]

    def clear_data(self):
        """Clear all stored data."""
        self.data = []

        # Clear the data file
        file_path = os.path.join(self.storage_directory, 'data.json')
        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('')  # Overwrite with empty content
                
    def get_state(self) -> dict:
        """Returns the current state of the data storage."""
        return {
            'max_capacity': self.max_capacity,
            'current_size': len(self.data),
            'storage_directory': self.storage_directory
        }
