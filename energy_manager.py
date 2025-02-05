# energy_manager.py

from typing import List
from .node import Node
from scipy.interpolate import CubicSpline
import numpy as np

class EnergyManager:
    @staticmethod
    def redistribute_energy(nodes: List[Node]):
        """
        Redistributes energy dynamically across nodes to ensure balance.
        """
        energy_levels = [node.energy for node in nodes]
        spline = CubicSpline(range(len(energy_levels)), energy_levels)
        smooth_energy = spline(np.linspace(0, len(energy_levels) - 1, len(energy_levels)))
        for i, node in enumerate(nodes):
            node.energy = max(smooth_energy[i], 0)
