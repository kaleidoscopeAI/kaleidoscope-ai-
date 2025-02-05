#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
import subprocess
from typing import Dict, Optional

class VenvLauncher:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'venv-launcher'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.default_terminal = self._detect_terminal()
        self.load_config()

    def _detect_terminal(self) -> str:
        terminals = ['gnome-terminal', 'konsole', 'xterm']
        for term in terminals:
            if subprocess.run(['which', term], capture_output=True).returncode == 0:
                return term
        return 'x-terminal-emulator'

    def load_config(self) -> None:
        if not self.config_file.exists():
            self.config = {'last_venv': '', 'terminal': self.default_terminal}
            self.save_config()
        else:
            self.config = json.loads(self.config_file.read_text())

    def save_config(self) -> None:
        self.config_file.write_text(json.dumps(self.config, indent=2))

    def launch_venv(self) -> None:
        venv_path = Path(self.config['last_venv']).expanduser()
        if not venv_path.exists():
            venv_path = self._find_nearest_venv()
        
        if venv_path and venv_path.exists():
            activate_script = venv_path / 'bin' / 'activate'
            if activate_script.exists():
                cmd = [self.config['terminal'], '--', 'bash', '-c', 
                      f'source {activate_script} && bash']
                subprocess.Popen(cmd)
                self.config['last_venv'] = str(venv_path)
                self.save_config()

    def _find_nearest_venv(self) -> Optional[Path]:
        current = Path.cwd()
        while current != Path('/'):
            venv = current / 'venv'
            if venv.exists() and (venv / 'bin' / 'activate').exists():
                return venv
            current = current.parent
        return None

if __name__ == '__main__':
    launcher = VenvLauncher()
    launcher.launch_venv()
