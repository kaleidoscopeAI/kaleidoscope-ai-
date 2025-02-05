import logging
import threading
from queue import Queue

# Configure logging for TaskDistributor
logging.basicConfig(
    filename="task_distributor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TaskDistributor:
    def __init__(self, num_workers=4):
        """
        Distributes tasks to worker nodes for parallel processing.

        Args:
            num_workers (int): Number of worker threads to create.
        """
        self.task_queue = Queue()
        self.num_workers = num_workers
        self.workers = []
        self.result_queue = Queue()

    def add_task(self, task):
        """
        Adds a task to the queue for processing.

        Args:
            task (function): Function to be executed as a task.

        Returns:
            None
        """
        self.task_queue.put(task)
        logging.info(f"Task added to queue: {task}")

    def start_workers(self):
        """
        Starts worker threads to process tasks from the queue.

        Returns:
            None
        """
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True  # Allow main thread to exit even if workers are running
            worker.start()
            self.workers.append(worker)
        logging.info(f"{self.num_workers} worker threads started.")

    def _worker(self):
        """
        Worker thread function to process tasks from the queue.

        Returns:
            None
        """
        while True:
            try:
                task = self.task_queue.get()
                result = task()  # Execute the task
                self.result_queue.put(result)
                logging.info(f"Task completed by worker: {task}")
            except Exception as e:
                logging.error(f"Error in worker thread: {e}")
            finally:
                self.task_queue.task_done()  # Indicate that the task is done

    def get_results(self):
        """
        Retrieves the results from the completed tasks.

        Returns:
            list: List of results from completed tasks.
        """
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results

    def wait_for_completion(self):
        """
        Waits for all tasks in the queue to be completed.

        Returns:
            None
        """
        self.task_queue.join()
        logging.info("All tasks completed.")

# Example usage
if __name__ == "__main__":
    distributor = TaskDistributor(num_workers=2)

    # Define some sample tasks
    def task1():
        # Simulate some work
        import time
        time.sleep(1)
        return "Result from task 1"

    def task2():
        # Simulate some work
        import time
        time.sleep(2)
        return "Result from task 2"

    # Add tasks to the queue
    distributor.add_task(task1)
    distributor.add_task(task2)

    # Start worker threads
    distributor.start_workers()

    # Wait for all tasks to complete
    distributor.wait_for_completion()

    # Get the results
    results = distributor.get_results()
    print("Results:", results)
