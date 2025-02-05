import numpy as np
import tensorflow as tf
from skimage.measure import marching_cubes
import plotly.graph_objects as go
from typing import Tuple, List, Optional
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
import torch
import torch.nn as nn

class EnhancedPerfectedCube:
    def __init__(self, resolution: int = 64, learning_rate: float = 0.001):
        self.resolution = resolution
        self.grid_spacing = 2.0 / resolution
        self.energy_density = np.zeros((resolution, resolution, resolution))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.learning_rate = learning_rate
        self.topology_optimizer = self._create_topology_optimizer()
        
    def _create_topology_optimizer(self) -> nn.Module:
        """Creates a neural network for topology optimization."""
        class TopologyOptimizer(nn.Module):
            def __init__(self, resolution):
                super().__init__()
                self.resolution = resolution
                self.conv3d_1 = nn.Conv3d(1, 16, kernel_size=3, padding=1)
                self.conv3d_2 = nn.Conv3d(16, 32, kernel_size=3, padding=1)
                self.conv3d_3 = nn.Conv3d(32, 1, kernel_size=3, padding=1)
                self.relu = nn.ReLU()
                
            def forward(self, x):
                x = self.relu(self.conv3d_1(x))
                x = self.relu(self.conv3d_2(x))
                return self.conv3d_3(x)
                
        return TopologyOptimizer(self.resolution).to(self.device)

    def compute_adaptive_gradients(self, scalar_field: np.ndarray) -> np.ndarray:
        """Compute gradients with adaptive step sizes based on field curvature."""
        gradients = np.zeros((self.resolution, self.resolution, self.resolution, 3))
        
        for i in range(1, self.resolution - 1):
            for j in range(1, self.resolution - 1):
                for k in range(1, self.resolution - 1):
                    # Compute local curvature
                    neighborhood = scalar_field[i-1:i+2, j-1:j+2, k-1:k+2]
                    curvature = np.abs(np.mean(np.gradient(neighborhood)))
                    
                    # Adapt step size based on curvature
                    h = self.grid_spacing * (1.0 / (1.0 + curvature))
                    
                    # Compute gradients
                    gradients[i,j,k] = np.array([
                        (scalar_field[i+1,j,k] - scalar_field[i-1,j,k]) / (2*h),
                        (scalar_field[i,j+1,k] - scalar_field[i,j-1,k]) / (2*h),
                        (scalar_field[i,j,k+1] - scalar_field[i,j,k-1]) / (2*h)
                    ])
                    
        return gradients

    def optimize_topology(self, iterations: int = 100) -> None:
        """Optimize the topology using the neural network with value range preservation."""
        print(f"Initial energy density range: [{self.energy_density.min():.3f}, {self.energy_density.max():.3f}]")
        optimizer = torch.optim.Adam(self.topology_optimizer.parameters(), 
                                   lr=self.learning_rate)
        
        energy_tensor = torch.from_numpy(self.energy_density).float().to(self.device)
        energy_tensor = energy_tensor.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
        
        for _ in range(iterations):
            optimizer.zero_grad()
            
            # Forward pass
            optimized_field = self.topology_optimizer(energy_tensor)
            
            # Compute loss using finite differences for gradients
            dx = optimized_field[..., 1:, :, :] - optimized_field[..., :-1, :, :]
            dy = optimized_field[..., :, 1:, :] - optimized_field[..., :, :-1, :]
            dz = optimized_field[..., :, :, 1:] - optimized_field[..., :, :, :-1]
            
            # Surface area approximation using gradient magnitudes
            surface_area = (torch.sum(torch.abs(dx)) + 
                          torch.sum(torch.abs(dy)) + 
                          torch.sum(torch.abs(dz)))
            
            # Volume preservation constraint
            volume_constraint = torch.abs(torch.mean(optimized_field) - 
                                       torch.mean(energy_tensor))
            
            # Add range constraint to keep values in a reasonable range
            range_constraint = torch.relu(torch.max(optimized_field) - 2.0) + \
                             torch.relu(-torch.min(optimized_field))
            
            loss = surface_area + 100.0 * volume_constraint + 1000.0 * range_constraint
            loss.backward()
            optimizer.step()
            
            if _ % 10 == 0:
                print(f"Iteration {_}: Loss = {loss.item():.3f}")
        
        # Update energy density with optimized field and ensure proper range
        self.energy_density = optimized_field.squeeze().detach().cpu().numpy()
        print(f"Final energy density range: [{self.energy_density.min():.3f}, {self.energy_density.max():.3f}]")

    def _march_cubes(self, scalar_field: np.ndarray, iso_level: float) -> Tuple[np.ndarray, np.ndarray]:
        """Enhanced marching cubes with topology optimization and adaptive sampling."""
        # Apply Gaussian smoothing to reduce noise
        smoothed_field = gaussian_filter(scalar_field, sigma=0.5)
        
        # Compute adaptive gradients
        gradients = self.compute_adaptive_gradients(smoothed_field)
        
        # Use gradient magnitude to adapt sampling
        gradient_mag = np.linalg.norm(gradients, axis=-1)
        adaptive_field = smoothed_field * (1.0 + 0.5 * gradient_mag)
        
        # Extract isosurface with marching cubes
        verts, faces, normals, values = marching_cubes(
            adaptive_field,
            level=iso_level,
            spacing=(self.grid_spacing, self.grid_spacing, self.grid_spacing),
            allow_degenerate=False
        )
        
        # Perform mesh optimization
        verts = self._optimize_mesh(verts, faces, normals)
        
        return verts, faces

    def _optimize_mesh(self, vertices: np.ndarray, faces: np.ndarray, 
                      normals: np.ndarray) -> np.ndarray:
        """Optimize mesh vertices using Laplacian smoothing and feature preservation."""
        # Build KD-tree for nearest neighbor queries
        tree = cKDTree(vertices)
        
        # Compute vertex weights based on curvature
        edges = set()
        for face in faces:
            for i in range(3):
                edge = tuple(sorted([face[i], face[(i+1)%3]]))
                edges.add(edge)
        
        weights = np.zeros(len(vertices))
        for v_idx in range(len(vertices)):
            # Find neighboring vertices
            neighbors = tree.query_ball_point(vertices[v_idx], self.grid_spacing * 2.0)
            if len(neighbors) > 1:
                # Compute local curvature
                local_normals = normals[neighbors]
                curvature = 1.0 - np.abs(np.mean(np.dot(local_normals, normals[v_idx])))
                weights[v_idx] = 1.0 / (1.0 + curvature)
        
        # Apply weighted Laplacian smoothing
        smoothed_vertices = vertices.copy()
        for _ in range(3):  # Number of smoothing iterations
            for v_idx in range(len(vertices)):
                neighbors = tree.query_ball_point(vertices[v_idx], self.grid_spacing * 2.0)
                if len(neighbors) > 1:
                    neighbor_positions = vertices[neighbors]
                    neighbor_weights = weights[neighbors]
                    smoothed_vertices[v_idx] = np.average(neighbor_positions, 
                                                        weights=neighbor_weights, axis=0)
        
        return smoothed_vertices

    def visualize(self, num_levels: int = 5, colormap: str = "Viridis"):
        """Enhanced visualization with multiple isosurfaces and advanced rendering."""
        fig = go.Figure()
        
        # Ensure data is properly normalized and handle edge cases
        data_min = np.min(self.energy_density)
        data_max = np.max(self.energy_density)
        
        if data_min == data_max:
            print("Warning: Uniform data field detected, adjusting visualization strategy")
            return
            
        # Add small epsilon to prevent numerical issues
        epsilon = (data_max - data_min) * 1e-5
        levels = np.linspace(data_min + epsilon, 
                           data_max - epsilon, 
                           num_levels)
        
        print(f"Generating isosurfaces at levels: {levels}")
        
        successful_surfaces = 0
        for level in levels:
            try:
                verts, faces = self._march_cubes(self.energy_density, level)
                
                # Skip if no vertices were generated
                if len(verts) == 0:
                    continue
                
                # Compute vertex colors based on gradient magnitude
                gradients = self.compute_adaptive_gradients(self.energy_density)
                gradient_mag = np.linalg.norm(gradients, axis=-1)
                vertex_colors = np.interp(gradient_mag.flatten(), 
                                        (gradient_mag.min(), gradient_mag.max()), 
                                        (0, 1))
                
                fig.add_trace(go.Mesh3d(
                    x=verts[:, 0],
                    y=verts[:, 1],
                    z=verts[:, 2],
                    i=faces[:, 0],
                    j=faces[:, 1],
                    k=faces[:, 2],
                    opacity=0.3,
                    colorscale=colormap,
                    intensity=vertex_colors,
                    lighting=dict(
                        ambient=0.3,
                        diffuse=0.7,
                        specular=0.2,
                        roughness=0.1
                    ),
                    lightposition=dict(x=100, y=200, z=150)
                ))
                successful_surfaces += 1
                
            except ValueError as e:
                print(f"Warning: Could not generate isosurface at level {level}: {str(e)}")
                continue
                
        if successful_surfaces == 0:
            print("Warning: No valid isosurfaces could be generated")
            return
            
        print(f"Successfully generated {successful_surfaces} isosurfaces")
        
        # Configure layout
        fig.update_layout(
            scene=dict(
                aspectmode='cube',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=False
        )
        
        fig.show()

if __name__ == "__main__":
    try:
        # Create instance with higher resolution
        pc = EnhancedPerfectedCube(resolution=64)
        print("Initialized PerfectedCube with resolution 64")
        
        # Generate interesting test data using a combination of geometric primitives
        x, y, z = np.mgrid[-1:1:64j, -1:1:64j, -1:1:64j]
        sphere = (x**2 + y**2 + z**2) < 0.5
        torus = ((np.sqrt(x**2 + y**2) - 0.7)**2 + z**2) < 0.1
        pc.energy_density = sphere.astype(float) + torus.astype(float)
        print("Generated test data with sphere and torus primitives")
        
        # Verify data shape and values
        print(f"Energy density shape: {pc.energy_density.shape}")
        print(f"Value range: [{pc.energy_density.min():.3f}, {pc.energy_density.max():.3f}]")
        
        # Optimize topology with progress monitoring
        print("\nStarting topology optimization...")
        pc.optimize_topology(iterations=50)
        print("Completed topology optimization")
        
        # Visualize with enhanced settings
        print("Generating visualization...")
        pc.visualize(num_levels=7, colormap="Plasma")
        print("Visualization complete")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")