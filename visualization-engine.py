# visualization/engine.py
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from rdkit import Chem
from rdkit.Chem import AllChem
from typing import Dict, List, Optional, Union
import torch
import torch.nn.functional as F

class AdvancedVisualizationEngine:
    """
    Advanced visualization engine combining quantum states, molecular structures,
    and neural network insights.
    """
    def __init__(self, canvas_size: tuple = (800, 600)):
        self.canvas_size = canvas_size
        self.color_schemes = {
            'quantum': 'Viridis',
            'molecular': 'Plasma',
            'neural': 'Magma',
            'energy': 'Inferno'
        }
        self.layout_options = self._create_default_layouts()

    def _create_default_layouts(self) -> Dict:
        """Create default layout configurations."""
        return {
            'quantum_state': {
                'title': 'Quantum State Visualization',
                'showlegend': True,
                'scene': {
                    'xaxis_title': 'State Index',
                    'yaxis_title': 'Amplitude',
                    'zaxis_title': 'Phase'
                }
            },
            'molecular': {
                'title': 'Molecular Structure Analysis',
                'showlegend': True,
                'scene': {
                    'xaxis_title': 'X',
                    'yaxis_title': 'Y',
                    'zaxis_title': 'Z'
                }
            }
        }

    def create_quantum_visualization(self, quantum_state: np.ndarray) -> go.Figure:
        """Create interactive 3D visualization of quantum state."""
        amplitudes = np.abs(quantum_state)
        phases = np.angle(quantum_state)
        
        fig = go.Figure(data=[
            go.Scatter3d(
                x=np.arange(len(quantum_state)),
                y=amplitudes,
                z=phases,
                mode='markers+lines',
                marker=dict(
                    size=10,
                    color=amplitudes,
                    colorscale=self.color_schemes['quantum'],
                    opacity=0.8
                ),
                name='Quantum State'
            )
        ])
        
        fig.update_layout(**self.layout_options['quantum_state'])
        return fig

    def create_molecular_visualization(self, mol: Chem.Mol) -> go.Figure:
        """Create 3D visualization of molecular structure with quantum properties."""
        # Generate 3D coordinates
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        
        # Get atomic coordinates
        conf = mol.GetConformer()
        positions = conf.GetPositions()
        
        # Create atom traces
        atoms_trace = go.Scatter3d(
            x=positions[:,0],
            y=positions[:,1],
            z=positions[:,2],
            mode='markers',
            marker=dict(
                size=8,
                color=[atom.GetAtomicNum() for atom in mol.GetAtoms()],
                colorscale=self.color_schemes['molecular'],
                opacity=0.8
            ),
            name='Atoms'
        )
        
        # Create bond traces
        bond_traces = []
        for bond in mol.GetBonds():
            id1 = bond.GetBeginAtomIdx()
            id2 = bond.GetEndAtomIdx()
            x = [positions[id1,0], positions[id2,0]]
            y = [positions[id1,1], positions[id2,1]]
            z = [positions[id1,2], positions[id2,2]]
            
            bond_traces.append(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color='grey', width=2),
                showlegend=False
            ))
        
        # Combine traces
        fig = go.Figure(data=[atoms_trace] + bond_traces)
        fig.update_layout(**self.layout_options['molecular'])
        return fig

    def create_network_visualization(self, 
                                  graph: nx.Graph, 
                                  node_data: Optional[Dict] = None) -> go.Figure:
        """Create interactive visualization of molecular/quantum network."""
        pos = nx.spring_layout(graph, dim=3)
        
        # Node trace
        node_x = [pos[node][0] for node in graph.nodes()]
        node_y = [pos[node][1] for node in graph.nodes()]
        node_z = [pos[node][2] for node in graph.nodes()]
        
        node_colors = []
        node_sizes = []
        node_text = []
        
        for node in graph.nodes():
            if node_data and node in node_data:
                node_colors.append(node_data[node].get('value', 0))
                node_sizes.append(node_data[node].get('size', 10))
                node_text.append(str(node_data[node].get('label', node)))
            else:
                node_colors.append(0)
                node_sizes.append(10)
                node_text.append(str(node))

        nodes_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                colorscale=self.color_schemes['neural'],
                opacity=0.8
            ),
            text=node_text,
            hoverinfo='text',
            name='Nodes'
        )
        
        # Edge trace
        edge_x = []
        edge_y = []
        edge_z = []
        
        for edge in graph.edges():
            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
            
        edges_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color='grey', width=1),
            hoverinfo='none',
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=[nodes_trace, edges_trace])
        fig.update_layout(
            title='Network Visualization',
            showlegend=True,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            )
        )
        
        return fig

    def create_energy_landscape(self, 
                              energies: np.ndarray, 
                              coordinates: np.ndarray) -> go.Figure:
        """Create visualization of quantum/molecular energy landscape."""
        # Create grid for surface plot
        x = np.linspace(min(coordinates[:,0]), max(coordinates[:,0]), 100)
        y = np.linspace(min(coordinates[:,1]), max(coordinates[:,1]), 100)
        X, Y = np.meshgrid(x, y)
        
        # Interpolate energies
        from scipy.interpolate import griddata
        Z = griddata((coordinates[:,0], coordinates[:,1]), 
                    energies, 
                    (X, Y), 
                    method='cubic')
        
        # Create surface plot
        fig = go.Figure(data=[
            go.Surface(
                x=X, y=Y, z=Z,
                colorscale=self.color_schemes['energy'],
                name='Energy Landscape'
            )
        ])
        
        # Add minima points
        minima_indices = self._find_local_minima(energies)
        minima_coords = coordinates[minima_indices]
        minima_energies = energies[minima_indices]
        
        fig.add_trace(go.Scatter3d(
            x=minima_coords[:,0],
            y=minima_coords[:,1],
            z=minima_energies,
            mode='markers',
            marker=dict(
                size=8,
                color='red',
                symbol='star'
            ),
            name='Energy Minima'
        ))
        
        fig.update_layout(
            title='Energy Landscape',
            scene=dict(
                xaxis_title='Coordinate 1',
                yaxis_title='Coordinate 2',
                zaxis_title='Energy'
            )
        )
        
        return fig

    def _find_local_minima(self, energies: np.ndarray) -> np.ndarray:
        """Find indices of local energy minima."""
        from scipy.signal import argrelextrema
        return argrelextrema(energies, np.less)[0]

    def create_interactive_dashboard(self, 
                                  quantum_data: Dict,
                                  molecular_data: Dict,
                                  network_data: Dict) -> go.Figure:
        """Create comprehensive interactive dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scene'}, {'type': 'scene'}],
                  [{'type': 'scene'}, {'type': 'scene'}]],
            subplot_titles=('Quantum State', 'Molecular Structure',
                          'Network Analysis', 'Energy Landscape')
        )
        
        # Add quantum state visualization
        quantum_fig = self.create_quantum_visualization(quantum_data['state'])
        fig.add_trace(quantum_fig.data[0], row=1, col=1)
        
        # Add molecular visualization
        mol_fig = self.create_molecular_visualization(molecular_data['molecule'])
        for trace in mol_fig.data:
            fig.add_trace(trace, row=1, col=2)
        
        # Add network visualization
        network_fig = self.create_network_visualization(
            network_data['graph'],
            network_data.get('node_data')
        )
        for trace in network_fig.data:
            fig.add_trace(trace, row=2, col=1)
        
        # Add energy landscape
        energy_fig = self.create_energy_landscape(
            network_data['energies'],
            network_data['coordinates']
        )
        fig.add_trace(energy_fig.data[0], row=2, col=2)
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1600,
            title_text="Quantum-Molecular Analysis Dashboard",
            showlegend=True
        )
        
        return fig
