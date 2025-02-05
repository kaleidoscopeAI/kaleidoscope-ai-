#!/bin/bash
set -euo pipefail

# Create launcher script
cat > ~/.local/bin/venv-launcher << 'EOF'
#!/usr/bin/env python3
import os
import json
from pathlib import Path
import subprocess

class VenvLauncher:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'venv-launcher'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.terminal = self._detect_terminal()
        self.load_config()

    def _detect_terminal(self):
        for term in ['gnome-terminal', 'konsole', 'xterm']:
            if subprocess.run(['which', term], capture_output=True).returncode == 0:
                return term
        return 'x-terminal-emulator'

    def load_config(self):
        if not self.config_file.exists():
            self.config = {'last_venv': '', 'terminal': self.terminal}
            self.save_config()
        else:
            self.config = json.loads(self.config_file.read_text())

    def save_config(self):
        self.config_file.write_text(json.dumps(self.config, indent=2))

    def find_venv(self):
        current = Path.cwd()
        while current != Path('/'):
            venv = current / 'venv'
            if venv.exists() and (venv / 'bin' / 'activate').exists():
                return venv
            current = current.parent
        return None

    def launch(self):
        venv_path = Path(self.config['last_venv']).expanduser()
        if not venv_path.exists():
            venv_path = self.find_venv()
        
        if venv_path and venv_path.exists():
            activate = venv_path / 'bin' / 'activate'
            if activate.exists():
                cmd = [self.terminal, '--', 'bash', '-c', 
                      f'source {activate} && exec bash']
                subprocess.Popen(cmd)
                self.config['last_venv'] = str(venv_path)
                self.save_config()

if __name__ == '__main__':
    VenvLauncher().launch()
EOF

mkdir -p ~/.local/bin
chmod +x ~/.local/bin/venv-launcher

# Create keyboard shortcut
mkdir -p ~/.config/autokey/data
cat > ~/.config/autokey/data/venv-launcher.txt << 'EOF'
keyboard.send_keys("<ctrl>+p")
system.exec_command("~/.local/bin/venv-launcher")
EOF

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 autokey-gtk xdotool

# Add to PATH if needed
grep -q '\.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Start autokey
autokey-gtk &

echo "Installation complete. Press Ctrl+P to launch Python venv."
echo "The script will auto-detect the nearest venv directory."
