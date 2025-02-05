import logging
import threading
from queue import Queue, Empty

# Configure logging for StreamHandler
logging.basicConfig(
    filename="stream_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class StreamHandler:
    def __init__(self, max_queue_size=1000):
        """
        Manages the streaming of data between components, ensuring synchronization and efficient processing.

        Args:
            max_queue_size (int): Maximum size for input and output streams.
        """
        self.input_stream = Queue(maxsize=max_queue_size)
        self.output_stream = Queue(maxsize=max_queue_size)
        self.is_active = False
        self.lock = threading.Lock()

    def start_streaming(self):
        """
        Activates the stream handler for data flow.

        Returns:
            None
        """
        with self.lock:
            self.is_active = True
        logging.info("Stream handler activated.")

    def ingest_data(self, data_packet):
        """
        Adds a data packet to the input stream.

        Args:
            data_packet (dict): Data to be streamed.

        Returns:
            None
        """
        try:
            with self.lock:
                self.input_stream.put(data_packet, timeout=2)
            logging.info(f"Data packet ingested: {data_packet}")
        except Exception as e:
            logging.error(f"Failed to ingest data packet: {data_packet}, Error: {e}")

    def forward_data(self, processing_function):
        """
        Processes and forwards data packets to the output stream.

        Args:
            processing_function (function): Function to process data packets.

        Returns:
            None
        """
        while self.is_active:
            try:
                with self.lock:
                    data_packet = self.input_stream.get(timeout=2)
                processed_packet = processing_function(data_packet)

                with self.lock:
                    self.output_stream.put(processed_packet, timeout=2)
                logging.info(f"Data packet forwarded: {processed_packet}")
            except Empty:
                logging.warning("Input stream is empty, waiting for data.")

            except Exception as e:
                logging.error(f"Error forwarding data packet: {e}")

    def retrieve_output(self):
        """
        Retrieves all data packets from the output stream.

        Returns:
            list: List of forwarded data packets.
        """
        with self.lock:
            output_data = []
            while not self.output_stream.empty():
                try:
                    output_data.append(self.output_stream.get_nowait())
                except Empty:
                    logging.warning("Output stream unexpectedly empty during retrieval.")
            logging.info("Output stream data retrieved.")
            return output_data

    def stop_streaming(self):
        """
        Deactivates the stream handler and stops data flow.
        Ensures all pending data is processed before shutting down.

        Returns:
            None
        """
        with self.lock:
            self.is_active = False
            # Ensure all data is processed
            while not self.input_stream.empty():
                try:
                    data_packet = self.input_stream.get_nowait()
                    logging.warning(f"Unprocessed data packet during shutdown: {data_packet}")
                except Empty:
                    break
            logging.info("Stream handler deactivated and input stream cleared.")

# Example usage
if __name__ == "__main__":
    handler = StreamHandler(max_queue_size=100)

    def sample_processing(packet):
        # Example transformation
        packet["status"] = "processed"
        return packet

    try:
        handler.start_streaming()

        # Simulate data ingestion
        handler.ingest_data({"id": 1, "value": 100})
        handler.ingest_data({"id": 2, "value": 200})

        # Process and forward data
        processing_thread = threading.Thread(target=handler.forward_data, args=(sample_processing,))
        processing_thread.start()

        # Simulate retrieval after processing
        import time
        time.sleep(1)  # Allow processing to complete
        output = handler.retrieve_output()
        print("Forwarded Data:", output)
    finally:
        handler.stop_streaming()
