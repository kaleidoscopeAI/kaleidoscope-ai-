data_processing/realtime/stream_handler.py
Python

import time
import queue
import threading

class StreamHandler:
    def __init__(self, data_processor: DataProcessor, batch_size: int = 10, processing_interval: float = 1.0):
        self.data_processor = data_processor
        self.batch_size = batch_size
        self.processing_interval = processing_interval
        self.data_queue = queue.Queue()
        self.is_running = False
        self.processing_thread = None

    def add_data(self, data):
        """Add data to the processing queue."""
        self.data_queue.put(data)

    def start_processing(self):
        """Start the data processing thread."""
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._process_data_loop)
            self.processing_thread.start()

    def stop_processing(self):
        """Stop the data processing thread."""
        if self.is_running:
            self.is_running = False
            if self.processing_thread:
                self.processing_thread.join()

    def _process_data_loop(self):
        """Continuously process data from the queue."""
        while self.is_running:
            batch = []
            while len(batch) < self.batch_size:
                try:
                    data = self.data_queue.get(timeout=self.processing_interval)
                    batch.append(data)
                except queue.Empty:
                    break  # No more data in the queue

            if batch:
                # Process the batch of data
                processed_data = self.data_processor.process_and_analyze(batch)
                # Handle the processed data (e.g., store it, visualize it, etc.)
                print("Processed Data:", processed_data)

            time.sleep(self.processing_interval)  # Wait for the next processing interval
            
    def get_state(self) -> dict:
        """Returns the current state of the stream handler."""
        return {
            'batch_size': self.batch_size,
            'processing_interval': self.processing_interval,
            'data_queue_size': self.data_queue.qsize(),
            'is_running': self.is_running
        }
