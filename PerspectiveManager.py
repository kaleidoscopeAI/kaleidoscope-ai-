
class PerspectiveManager:
    def __init__(self):
        self.perspectives = []  # Store perspectives dynamically

    def add_perspective(self, name, function):
        """
        Add a new perspective to the manager.
        :param name: Name of the perspective.
        :param function: A callable that defines the perspective logic.
        """
        self.perspectives.append({"name": name, "function": function})
        print(f"Perspective '{name}' has been added.")

    def process_perspectives(self, data):
        """
        Apply all perspectives to the given data.
        :param data: Input data to process.
        :return: A dictionary of results from each perspective.
        """
        print("Processing data through multiple perspectives...")
        results = {}
        for perspective in self.perspectives:
            name = perspective["name"]
            function = perspective["function"]
            try:
                results[name] = function(data)
                print(f"Processed perspective '{name}'.")
            except Exception as e:
                print(f"Error processing perspective '{name}': {e}")
        return results

# Example usage of PerspectiveManager
if __name__ == "__main__":
    def example_perspective(data):
        return data[::-1]  # Example: Reverse the data

    perspective_manager = PerspectiveManager()
    perspective_manager.add_perspective("Reverse Perspective", example_perspective)
    sample_data = "Kaleidoscope Example"
    print(perspective_manager.process_perspectives(sample_data))
