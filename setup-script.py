import os
import sys
import subprocess
import logging
from typing import Dict, List
import json

class BioSystemSetup:
    def __init__(self):
        self.logger = logging.getLogger("BioSystemSetup")
        self.config = {
            "data_dir": "bio_data",
            "log_dir": "logs",
            "required_packages": [
                "numpy",
                "networkx",
                "pandas",
                "flask"
            ]
        }

    def setup(self):
        """Run complete setup process"""
        try:
            self._create_directories()
            self._install_requirements()
            self._initialize_system()
            return True
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _create_directories(self):
        """Create necessary directories"""
        for dir_name in [self.config["data_dir"], self.config["log_dir"]]:
            os.makedirs(dir_name, exist_ok=True)
            self.logger.info(f"Created directory: {dir_name}")

    def _install_requirements(self):
        """Install required packages"""
        for package in self.config["required_packages"]:
            try:
                subprocess.check_call([
                    sys.executable, 
                    "-m", 
                    "pip", 
                    "install", 
                    package
                ])
                self.logger.info(f"Installed {package}")
            except subprocess.CalledProcessError:
                self.logger.error(f"Failed to install {package}")

    def _initialize_system(self):
        """Initialize the bio system"""
        self._create_initial_config()
        self._setup_logging()
        self._create_test_data()

    def _create_initial_config(self):
        """Create initial configuration file"""
        config = {
            "cell_params": {
                "initial_capacity": 100,
                "membrane_permeability": 0.7,
                "energy_efficiency": 0.8
            },
            "visualization": {
                "update_interval": 1000,
                "max_history": 1000
            }
        }
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=os.path.join(self.config["log_dir"], "bio_system.log"),
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _create_test_data(self):
        """Create sample test data"""
        test_data = {
            "sequence_1": {
                "value": 42,
                "type": "numeric",
                "metadata": {"source": "sensor"}
            },
            "sequence_2": {
                "value": 75,
                "type": "numeric",
                "metadata": {"source": "external"}
            }
        }
        
        with open(os.path.join(self.config["data_dir"], "test_data.json"), "w") as f:
            json.dump(test_data, f, indent=2)

def run_setup():
    """Run the setup process"""
    setup = BioSystemSetup()
    if setup.setup():
        print("Bio System setup completed successfully!")
        print("""
        To start the system:
        1. Run 'python bio_system.py' to start the backend
        2. Open 'http://localhost:5000' in your browser to view the dashboard
        """)
    else:
        print("Setup failed. Check logs for details.")

if __name__ == "__main__":
    run_setup()