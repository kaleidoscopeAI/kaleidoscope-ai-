import os
import sys

class ModuleLocator:
    """
    Dynamically locates modules and scripts in the Kaleidoscope AI project.
    """
    @staticmethod
    def add_to_sys_path(base_path: str = "."):
        """
        Adds all directories in the project to sys.path for dynamic imports.
        """
        for root, dirs, files in os.walk(base_path):
            if root not in sys.path:
                sys.path.append(root)

    @staticmethod
    def resolve_module(module_name: str):
        """
        Attempts to import the specified module dynamically.
        """
        try:
            return __import__(module_name)
        except ImportError as e:
            print(f"Failed to import module '{module_name}': {e}")
            return None

if __name__ == "__main__":
    # Automatically resolve and add paths to sys.path
    print("Configuring module paths...")
    ModuleLocator.add_to_sys_path()
    print("Module paths configured successfully.")
