# deployment/build_system.py
import os
import sys
import shutil
import subprocess
import venv
import json
from pathlib import Path
import platform
import zipfile
import hashlib
from typing import Dict, List

class SystemBuilder:
    """Builds and packages the complete system for deployment."""
    
    def __init__(self, target_dir: str = "dist"):
        self.target_dir = Path(target_dir)
        self.source_dir = Path(os.path.dirname(os.path.dirname(__file__)))
        self.build_dir = self.target_dir / "build"
        self.dist_dir = self.target_dir / "dist"
        self.venv_dir = self.build_dir / "venv"
        
        # System components
        self.required_dirs = [
            "core",
            "specialized",
            "visualization",
            "gui",
            "tests",
            "data"
        ]
        
    def build(self):
        """Build the complete system."""
        print("Starting system build...")
        
        # Create directories
        self._create_directories()
        
        # Copy source files
        self._copy_source_files()
        
        # Create virtual environment
        self._create_virtual_environment()
        
        # Install dependencies
        self._install_dependencies()
        
        # Run tests
        self._run_tests()
        
        # Create deployable package
        self._create_package()
        
        print("Build completed successfully!")
        
    def _create_directories(self):
        """Create necessary directories."""
        print("Creating directories...")
        for dir_name in [self.build_dir, self.dist_dir]:
            dir_name.mkdir(parents=True, exist_ok=True)
            
        for component in self.required_dirs:
            (self.build_dir / component).mkdir(parents=True, exist_ok=True)

    def _copy_source_files(self):
        """Copy source files to build directory."""
        print("Copying source files...")
        
        def copy_recursively(src: Path, dst: Path):
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                for item in src.iterdir():
                    if item.name.startswith('.'):
                        continue
                    d = dst / item.name
                    if item.is_dir():
                        d.mkdir(exist_ok=True)
                        copy_recursively(item, d)
                    else:
                        shutil.copy2(item, d)
        
        for component in self.required_dirs:
            src = self.source_dir / component
            if src.exists():
                copy_recursively(src, self.build_dir / component)

    def _create_virtual_environment(self):
        """Create and configure virtual environment."""
        print("Creating virtual environment...")
        venv.create(self.venv_dir, with_pip=True)
        
    def _install_dependencies(self):
        """Install system dependencies."""
        print("Installing dependencies...")
        pip_path = str(self.venv_dir / "Scripts" / "pip.exe" if platform.system() == "Windows" 
                      else self.venv_dir / "bin" / "pip")
        
        requirements = [
            "numpy>=1.21.0",
            "scipy>=1.7.0",
            "networkx>=2.6.0",
            "matplotlib>=3.4.0",
            "PyQt5>=5.15.0",
            "rdkit>=2021.03.1",
            "plotly>=5.3.1",
            "pandas>=1.3.0",
            "torch>=1.9.0",
            "scikit-learn>=0.24.2"
        ]
        
        requirements_file = self.build_dir / "requirements.txt"
        with open(requirements_file, "w") as f:
            f.write("\n".join(requirements))
            
        subprocess.check_call([pip_path, "install", "-r", str(requirements_file)])

    def _run_tests(self):
        """Run system tests."""
        print("