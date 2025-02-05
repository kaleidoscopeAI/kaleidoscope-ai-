# preprocessing/data_processor.py

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
import pandas as pd
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import torch
from sklearn.preprocessing import StandardScaler

class DataPreprocessor:
    """
    Advanced data preprocessing for quantum-molecular analysis.
    Handles multiple input formats and prepares data for analysis.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.scalers = {}
        self.feature_cache = {}
        self.supported_formats = {
            'smiles': self._process_smiles,
            'sdf': self._process_sdf,
            'pdb': self._process_pdb,
            'csv': self._process_csv,
            'json': self._process_json
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load preprocessing configuration."""
        default_config = {
            'feature_scaling': True,
            'feature_selection': ['MolWeight', 'LogP', 'TPSA', 'HBondDonors'],
            'max_atoms': 100,
            'quantum_features': True,
            'cache_features': True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
        
    def process_data(self, 
                    data: Union[str, Path, List[str]], 
                    data_type: str) -> Dict:
        """
        Process input data based on type.
        
        Args:
            data: Input data (file path, SMILES string, or list)
            data_type: Type of input data ('smiles', 'sdf', etc.)
            
        Returns:
            Processed data dictionary
        """
        if data_type not in self.supported_formats:
            raise ValueError(f"Unsupported data type: {data_type}")
            
        processor = self.supported_formats[data_type]
        return processor(data)
        
    def _process_smiles(self, smiles_data: Union[str, List[str]]) -> Dict:
        """Process SMILES input data."""
        if isinstance(smiles_data, str):
            smiles_list = [smiles_data]
        else:
            smiles_list = smiles_data
            
        processed_data = {
            'molecules': [],
            'features': [],
            'quantum_states': [],
            'metadata': {
                'type': 'smiles',
                'count': len(smiles_list)
            }
        }
        
        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    continue
                    
                # Generate 3D conformation
                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=42)
                AllChem.MMFFOptimizeMolecule(mol)
                
                # Calculate features
                features = self._calculate_molecular_features(mol)
                
                # Generate quantum state if enabled
                quantum_state = None
                if self.config['quantum_features']:
                    quantum_state = self._generate_quantum_state(mol)
                
                processed_data['molecules'].append(mol)
                processed_data['features'].append(features)
                if quantum_state is not None:
                    processed_data['quantum_states'].append(quantum_state)
                    
            except Exception as e:
                print(f"Error processing SMILES {smiles}: {str(e)}")
                
        # Scale features if enabled
        if self.config['feature_scaling'] and processed_data['features']:
            processed_data['features'] = self._scale_features(processed_data['features'])
            
        return processed_data
        
    def _calculate_molecular_features(self, mol: Chem.Mol) -> Dict:
        """Calculate molecular features."""
        features = {}
        
        # Calculate basic descriptors
        features.update({
            'MolWeight': Descriptors.ExactMolWt(mol),
            'LogP': Descriptors.MolLogP(mol),
            'TPSA': Descriptors.TPSA(mol),
            'HBondDonors': rdMolDescriptors.CalcNumHBD(mol),
            'HBondAcceptors': rdMolDescriptors.CalcNumHBA(mol),
            'RotatableBonds': Descriptors.NumRotatableBonds(mol),
            'RingCount': rdMolDescriptors.CalcNumRings(mol),
            'AromaticRings': rdMolDescriptors.CalcNumAromaticRings(mol)
        })
        
        # Calculate fingerprints
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
        features['fingerprint'] = list(fp.ToBitString())
        
        # Filter features based on config
        if self.config['feature_selection']:
            features = {k: v for k, v in features.items() 
                      if k in self.config['feature_selection']}
            
        return features
        
    def _generate_quantum_state(self, mol: Chem.Mol) -> Optional[np.ndarray]:
        """Generate quantum state representation of molecule."""
        if mol.GetNumAtoms() > self.config['max_atoms']:
            return None
            
        # Get atomic positions
        conf = mol.GetConformer()
        positions = conf.GetPositions()
        
        # Create quantum state
        n_atoms = mol.GetNumAtoms()
        quantum_dim = 2 ** (n_atoms.bit_length())
        state = np.zeros(quantum_dim, dtype=complex)
        
        for i, pos in enumerate(positions):
            if i < quantum_dim:
                phase = np.exp(2j * np.pi * np.sum(pos) / 30.0)
                state[i] = phase
                
        return state / np.linalg.norm(state)
        
    def _scale_features(self, features: List[Dict]) -> List[Dict]:
        """Scale numerical features."""
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(features)
        
        # Separate numerical and non-numerical columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        
        # Scale numerical features
        if not self.scalers:
            self.scalers = {col: StandardScaler() for col in num_cols}
            
        for col in num_cols:
            df[col] = self.scalers[col].fit_transform(df[[col]])
            
        return df.to_dict('records')
        
    def _process_sdf(self, sdf_path: Union[str, Path]) -> Dict:
        """Process SDF file."""
        supplier = Chem.SDMolSupplier(str(sdf_path))
        smiles_list = [Chem.MolToSmiles(mol) for mol in supplier if mol is not None]
        return self._process_smiles(smiles_list)
        
    def _process_pdb(self, pdb_path: Union[str, Path]) -> Dict:
        """Process PDB file."""
        mol = Chem.MolFromPDBFile(str(pdb_path))
        if mol is None:
            raise ValueError("Failed to parse PDB file")
        return self._process_smiles(Chem.MolToSmiles(mol))
        
    def _process_csv(self, csv_path: Union[str, Path]) -> Dict:
        """Process CSV file containing SMILES data."""
        df = pd.read_csv(csv_path)
        
        # Try to find SMILES column
        smiles_col = None
        for col in df.columns:
            if 'SMILES' in col.upper():
                smiles_col = col
                break
                
        if smiles_col is None:
            raise ValueError("No SMILES column found in CSV")
            
        return self._process_smiles(df[smiles_col].tolist())
        
    def _process_json(self, json_path: Union[str, Path]) -> Dict:
        """Process JSON file containing molecular data."""
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            if all(isinstance(x, str) for x in data):
                return self._process_smiles(data)
            else:
                raise ValueError("JSON must contain list of SMILES strings")
        elif isinstance(data, dict) and 'smiles' in data:
            return self._process_smiles(data['smiles'])
        else:
            raise ValueError("Unsupported JSON format")

    def save_preprocessor(self, path: Union[