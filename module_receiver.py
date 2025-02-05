class ModuleReceiver:
    """
    A base class for components in the Kaleidoscope AI system that interact with dynamically resolved modules.
    Provides mechanisms for seamless communication and initialization.
    """

    def __init__(self):
        self.received_modules = {}

    def register_module(self, module_name: str, module_instance):
        """
        Registers a dynamically loaded module instance for use within the receiver.
        :param module_name: The name of the module being registered.
        :param module_instance: The instance of the module to register.
        """
        if module_name in self.received_modules:
            print(f"Warning: Module '{module_name}' is already registered. Overwriting.")

        self.received_modules[module_name] = module_instance
        print(f"Module '{module_name}' registered successfully.")

    def get_module(self, module_name: str):
        """
        Retrieves a previously registered module instance.
        :param module_name: The name of the module to retrieve.
        :return: The registered module instance or None if not found.
        """
        return self.received_modules.get(module_name, None)

# Example usage
if __name__ == "__main__":
    receiver = ModuleReceiver()

    # Simulated dynamically loaded modules
    class MockResourceManager:
        pass

    class MockTaskManager:
        pass

    receiver.register_module("ResourceManager", MockResourceManager())
    receiver.register_module("TaskManager", MockTaskManager())

    resource_manager = receiver.get_module("ResourceManager")
    task_manager = receiver.get_module("TaskManager")

    print("Retrieved Modules:", resource_manager, task_manager)
