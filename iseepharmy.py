import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from scipy.spatial import ConvexHull
from scipy.stats import gaussian_kde
from typing import Dict, List, Optional, Tuple
import torch
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from Bio.PDB import *
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

class DrugDiscoveryAnalyzer:
    def __init__(self, output_dir: str = "analysis_output"):
        self.output_dir = output_dir
        self.interaction_network = nx.Graph()
        self.color_scheme = sns.color_palette("husl", 8)

    def analyze_results(self, results: List[Dict]) -> Dict:
        analysis = {
            'quantum_analysis': self._analyze_quantum_properties(results),
            'binding_analysis': self._analyze_binding_patterns(results),
            'chemical_space': self._analyze_chemical_space(results),
            'structure_activity': self._analyze_structure_activity(results),
            'interaction_network': self._build_interaction_network(results)
        }

        self._generate_visualizations(analysis, results)
        return analysis

    def _analyze_quantum_properties(self, results: List[Dict]) -> Dict:
        quantum_data = {'wavefunction_overlaps': [], 'phase_coherence': [], 'entanglement_metrics': [], 'energy_distributions': []}

        for result in results:
            quantum_data['wavefunction_overlaps'].extend(result.get('wavefunction_overlap', []))
            quantum_data['phase_coherence'].extend(result.get('phase_coherence', []))
            quantum_data['entanglement_metrics'].extend(result.get('entanglement', []))
            quantum_data['energy_distributions'].extend(result.get('binding_energy', []))

        analysis = {key: np.mean(values) if values else 0 for key, values in quantum_data.items()}
        return analysis

    def _analyze_binding_patterns(self, results: List[Dict]) -> Dict:
        binding_data = {'site_preferences': {}, 'interaction_profiles': []}

        for result in results:
            binding_data['interaction_profiles'].append(result.get('interaction_profile', {}))

        if binding_data['interaction_profiles']:
            binding_data['site_preferences'] = {
                key: sum(profile.get(key, 0) for profile in binding_data['interaction_profiles'])
                for key in binding_data['interaction_profiles'][0]
            }
        return binding_data

    def _analyze_chemical_space(self, results: List[Dict]) -> Dict:
        features = np.array([result.get('features', []) for result in results if 'features' in result])

        if features.size == 0:
            return {'pca_coordinates': [], 'tsne_coordinates': []}

        pca = PCA(n_components=3)
        pca_coords = pca.fit_transform(features)

        tsne = TSNE(n_components=2, perplexity=30)
        tsne_coords = tsne.fit_transform(features)

        return {'pca_coordinates': pca_coords, 'tsne_coordinates': tsne_coords}

    def _analyze_structure_activity(self, results: List[Dict]) -> Dict:
        activities = [result.get('activity_score', 0) for result in results if 'activity_score' in result]
        fingerprints = [result.get('fingerprint', []) for result in results if 'fingerprint' in result]

        if not activities or not fingerprints:
            return {'feature_importance': [], 'activity_prediction_score': 0}

        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=100)
        model.fit(fingerprints, activities)

        feature_importance = model.feature_importances_
        return {'feature_importance': feature_importance, 'activity_prediction_score': model.score(fingerprints, activities)}

    def _build_interaction_network(self, results: List[Dict]) -> nx.Graph:
        G = nx.Graph()

        for result in results:
            compound_id = result.get('compound_id')
            if compound_id:
                G.add_node(compound_id, weight=result.get('activity_score', 0))
                for interaction in result.get('interactions', []):
                    G.add_edge(compound_id, interaction.get('target_id'), weight=interaction.get('interaction_score', 0))

        return G

    def _generate_visualizations(self, analysis: Dict, results: List[Dict]):
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        axs[0].hist(analysis['quantum_analysis'].get('energy_distributions', []), bins=20, color='blue')
        axs[0].set_title('Energy Distributions')

        tsne_coords = analysis['chemical_space'].get('tsne_coordinates')
        if tsne_coords:
            axs[1].scatter(tsne_coords[:, 0], tsne_coords[:, 1], c='red')
        axs[1].set_title('t-SNE Visualization')

        nx.draw(analysis['interaction_network'], with_labels=True, node_color='green', edge_color='gray', ax=axs[2])
        axs[2].set_title('Interaction Network')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/visualization.png")
