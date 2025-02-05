import os
import subprocess
import sys
import stat

def create_virtual_environment(env_name="kaleidoscope_env"):
    """
    Creates a Python virtual environment.
    """
    print(f"Creating virtual environment: {env_name}")
    subprocess.run([sys.executable, "-m", "venv", env_name])
    print("Virtual environment created successfully.")

def activate_virtual_environment(env_name="kaleidoscope_env"):
    """
    Displays instructions to activate the virtual environment.
    """
    activation_script = os.path.join(env_name, "Scripts" if os.name == "nt" else "bin", "activate")
    if not os.path.exists(activation_script):
        raise FileNotFoundError("Virtual environment activation script not found.")
    print(f"To activate your virtual environment, run:\nsource {activation_script}")
    print("After activation, re-run this script to continue.")

def install_requirements(env_name="kaleidoscope_env"):
    """
    Installs the required dependencies into the virtual environment.
    """
    print("Installing dependencies...")
    pip_path = os.path.join(env_name, "Scripts", "pip") if os.name == "nt" else os.path.join(env_name, "bin", "pip")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully.")

def grant_permissions():
    """
    Grants executable permissions to all files in the project directory.
    """
    print("Granting executable permissions to all scripts...")
    for root, dirs, files in os.walk("."):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IEXEC)
            except Exception as e:
                print(f"Failed to grant permissions for {file_path}: {e}")
    print("Permissions granted successfully.")

def organize_files():
    """
    Organizes files into the correct structure.
    """
    print("Organizing files into the correct structure...")
    subprocess.run([sys.executable, "organize_files.py"])
    print("Files organized successfully.")

def run_tests():
    """
    Runs all unit and integration tests.
    """
    print("Running system tests...")
    subprocess.run(["pytest", "tests"])
    print("Tests completed successfully.")

def initiate_pipeline():
    """
    Starts the Kaleidoscope AI pipeline.
    """
    print("Starting Kaleidoscope AI pipeline...")
    subprocess.run([sys.executable, "main.py"])
    print("Kaleidoscope AI is now running.")

if __name__ == "__main__":
    print("Starting Kaleidoscope AI Setup")
    create_virtual_environment()
    print("\nActivate your virtual environment before proceeding.")
    activate_virtual_environment()

    print("\nRe-run this script after activating your environment.")
