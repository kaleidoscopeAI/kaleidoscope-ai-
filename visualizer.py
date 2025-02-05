import plotly.graph_objects as go
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

class Visualizer:
    def __init__(self):
        self.current_fig = None
        self.setup_colors()

    def setup_colors(self):
        self.atom_colors = {
            'C': '#808080',  # Gray
            'H': '#FFFFFF',  # White
            'O': '#FF0000',  # Red
            'N': '#0000FF',  # Blue
            'P': '#FFA500',  # Orange
            'S': '#FFFF00',  # Yellow
        }

    def show_molecule(self, mol):
        if not mol:
            return
            
        fig = go.Figure()
        
        # Get 3D coordinates
        conf = mol.GetConformer()
        positions = np.array([[conf.GetAtomPosition(i).