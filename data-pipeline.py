import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.preprocessing import StandardScaler, RobustScaler
import networkx as nx
from rdkit import Chem
from rdkit.Chem import AllChem
import threading
from queue import Queue
import asyncio
import aiohttp
import websockets
import json
import time
from collections import defaultdict, deque
import logging
import h5py

class DataIngestionPipeline:
    def __init__(self, buffer_size: int = 10000):
        self.market_buffer = Queue(maxsize=buffer_size)
        self.molecule_buffer = Queue(maxsize=buffer_size)
        self.sensor_buffer = Queue(maxsize=buffer_size)
        self.scalers = {
            'market': RobustScaler(),
            'molecule': StandardScaler(),
            'sensor': StandardScaler()
        }
        self.feature_extractors = {
            'market': self._extract_market_features,
            'molecule': self._extract_molecular_features,
            'sensor': self._extract_sensor_features
        }
        self.lock = threading.Lock()
        
    async def ingest_market_data(self, websocket_url: str):
        async with websockets.connect(websocket_url) as websocket:
            while True:
                data = await websocket.recv()
                parsed_data = json.loads(data)
                features = self._extract_market_features(parsed_data)
                await self.market_buffer.put(features)

    def _extract_market_features(self, data: Dict) -> np.ndarray:
        price_data = np.array(data['prices'])
        volume_data = np.array(data['volumes'])
        
        # Technical indicators
        sma = np.convolve(price_data, np.ones(20)/20, mode='valid')
        ema = pd.Series(price_data).ewm(span=20).mean().values
        rsi = self._calculate_rsi(price_data)
        
        # Momentum indicators
        momentum = price_data[1:] - price_data[:-1]
        macd = self._calculate_macd(price_data)
        
        # Volatility features
        returns = np.diff(np.log(price_data))
        volatility = np.std(returns, ddof=1)
        
        features = np.concatenate([
            price_data, volume_data, sma, ema, rsi, momentum, macd,
            np.array([volatility] * len(price_data))
        ])
        
        return self.scalers['market'].fit_transform(features.reshape(-1, 1)).flatten()

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.convolve(gain, np.ones(period)/period, mode='valid')
        avg_loss = np.convolve(loss, np.ones(period)/period, mode='valid')
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return np.pad(rsi, (period-1, 0), mode='edge')

    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> np.ndarray:
        fast_ema = pd.Series(prices).ewm(span=fast).mean()
        slow_ema = pd.Series(prices).ewm(span=slow).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal).mean()
        return (macd_line - signal_line).values

    async def ingest_molecular_data(self, molecule_stream: str):
        while True:
            mol = Chem.MolFromSmiles(molecule_stream)
            if mol is not None:
                features = self._extract_molecular_features(mol)
                await self.molecule_buffer.put(features)

    def _extract_molecular_features(self, mol: Chem.Mol) -> np.ndarray:
        # Topological features
        num_atoms = mol.GetNumAtoms()
        num_bonds = mol.GetNumBonds()
        
        # Calculate 2D fingerprints
        morgan_fp = np.array(AllChem.GetMorganFingerprintAsBitVect(mol, 2))
        maccs_fp = np.array(AllChem.GetMACCSKeysFingerprint(mol))
        
        # Geometric features
        try:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            conf = mol.GetConformer()
            positions = conf.GetPositions()
            
            distances = []
            for i in range(num_atoms):
                for j in range(i+1, num_atoms):
                    pos1 = positions[i]
                    pos2 = positions[j]
                    distance = np.linalg.norm(pos1 - pos2)
                    distances.append(distance)
            
            geometric_features = np.array([
                np.mean(distances),
                np.std(distances),
                np.max(distances),
                np.min(distances)
            ])
            
        except:
            geometric_features = np.zeros(4)
        
        features = np.concatenate([
            morgan_fp, maccs_fp, geometric_features,
            [num_atoms, num_bonds]
        ])
        
        return self.scalers['molecule'].fit_transform(features.reshape(-1, 1)).flatten()

    async def ingest_sensor_data(self, sensor_port: str):
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(f'http://localhost:{sensor_port}/sensor_data') as response:
                    data = await response.json()
                    features = self._extract_sensor_features(data)
                    await self.sensor_buffer.put(features)

    def _extract_sensor_features(self, data: Dict) -> np.ndarray:
        depth_map = np.array(data['depth_map'])
        position = np.array(data['position'])
        velocity = np.array(data['velocity'])
        
        # Process depth map
        filtered_depth = savgol_filter(depth_map, window_length=5, polyorder=2)
        depth_gradient = np.gradient(filtered_depth)
        
        # Motion features
        acceleration = np.gradient(velocity)
        jerk = np.gradient(acceleration)
        
        # Combined features
        features = np.concatenate([
            filtered_depth.flatten(),
            depth_gradient.flatten(),
            position,
            velocity,
            acceleration,
            jerk
        ])
        
        return self.scalers['sensor'].fit_transform(features.reshape(-1, 1)).flatten()

    def save_to_disk(self, filepath: str):
        with h5py.File(filepath, 'w') as f:
            # Save market data
            market_data = []
            while not self.market_buffer.empty():
                market_data.append(self.market_buffer.get())
            f.create_dataset('market_data', data=np.array(market_data))
            
            # Save molecular data
            molecule_data = []
            while not self.molecule_buffer.empty():
                molecule_data.append(self.molecule_buffer.get())
            f.create_dataset('molecule_data', data=np.array(molecule_data))
            
            # Save sensor data
            sensor_data = []
            while not self.sensor_buffer.empty():
                sensor_data.append(self.sensor_buffer.get())
            f.create_dataset('sensor_data', data=np.array(sensor_data))
            
            # Save scaler parameters
            for domain, scaler in self.scalers.items():
                grp = f.create_group(f'{domain}_scaler')
                for param_name, param_value in scaler.get_params().items():
                    grp.attrs[param_name] = param_value

    def load_from_disk(self, filepath: str):
        with h5py.File(filepath, 'r') as f:
            # Load market data
            market_data = f['market_data'][:]
            for data in market_data:
                self.market_buffer.put(data)
            
            # Load molecular data
            molecule_data = f['molecule_data'][:]
            for data in molecule_data:
                self.molecule_buffer.put(data)
            
            # Load sensor data
            sensor_data = f['sensor_data'][:]
            for data in sensor_data:
                self.sensor_buffer.put(data)
            
            # Load scaler parameters
            for domain in self.scalers:
                grp = f[f'{domain}_scaler']
                params = dict(grp.attrs)
                self.scalers[domain].set_params(**params)

class DataBatch:
    def __init__(
        self,
        market_data: Optional[torch.Tensor] = None,
        molecule_data: Optional[torch.Tensor] = None,
        sensor_data: Optional[torch.Tensor] = None
    ):
        self.market_data = market_data
        self.molecule_data = molecule_data
        self.sensor_data = sensor_data
        
    def to_device(self, device: torch.device):
        if self.market_data is not None:
            self.market_data = self.market_data.to(device)
        if self.molecule_data is not None:
            self.molecule_data = self.molecule_data.to(device)
        if self.sensor_data is not None:
            self.sensor_data = self.sensor_data.to(device)
        return self

class MultiDomainDataset(Dataset):
    def __init__(self, data_pipeline: DataIngestionPipeline, batch_size: int = 32):
        self.pipeline = data_pipeline
        self.batch_size = batch_size
        
    def __len__(self):
        return min(
            self.pipeline.market_buffer.qsize(),
            self.pipeline.molecule_buffer.qsize(),
            self.pipeline.sensor_buffer.qsize()
        ) // self.batch_size
        
    def __getitem__(self, idx: int) -> DataBatch:
        market_batch = []
        molecule_batch = []
        sensor_batch = []
        
        for _ in range(self.batch_size):
            if not self.pipeline.market_buffer.empty():
                market_batch.append(self.pipeline.market_buffer.get())
            if not self.pipeline.molecule_buffer.empty():
                molecule_batch.append(self.pipeline.molecule_buffer.get())
            if not self.pipeline.sensor_buffer.empty():
                sensor_batch.append(self.pipeline.sensor_buffer.get())
                
        return DataBatch(
            market_data=torch.tensor(market_batch) if market_batch else None,
            molecule_data=torch.tensor(molecule_batch) if molecule_batch else None,
            sensor_data=torch.tensor(sensor_batch) if sensor_batch else None
        )
