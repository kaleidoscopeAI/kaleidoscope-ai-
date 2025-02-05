import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.transform import Rotation
import plotly.colors as colors

class RefinedMolecularGrid:
    def __init__(self, resolution: int = 12):
        self.resolution = resolution
        self.grid_points = resolution + 1
        self.atoms = []
        self.orbital_coefficients = {
            'H': {'1s': 1.0},
            'O': {'2s': 2.0, '2p': 4.0},
            'C': {'2s': 2.0, '2p': 2.0},
            'N': {'2s': 2.0, '2p': 3.0}
        }
        
    def gaussian_orbital(self, r, n, l, zeta):
        """
        Compute Gaussian-type orbital.
        r: distance from nucleus
        n: principal quantum number
        l: angular momentum quantum number
        zeta: orbital exponent
        """
        norm = (2*zeta)**(n+0.5) / np.sqrt(np.math.factorial(2*n))
        return norm * r**(l) * np.exp(-zeta * r**2)

    def compute_electron_density(self, point):
        """Compute electron density using gaussian orbitals."""
        density = 0
        for atom in self.atoms:
            pos = np.array(atom['position'])
            r = np.linalg.norm(point - pos)
            
            # Get orbital coefficients for this atom type
            orbitals = self.orbital_coefficients.get(atom['type'], {'1s': 1.0})
            
            for orbital, coeff in orbitals.items():
                n = int(orbital[0])
                l = 0 if orbital[1] == 's' else 1  # simplified for s and p orbitals
                zeta = 1.0 / (n * n)  # simplified Slater's rules
                density += coeff * self.gaussian_orbital(r, n-1, l, zeta)
        
        return density

    def create_deformed_grid(self):
        """Create a deformed grid based on electron density."""
        # Create base coordinates
        coords = np.linspace(-1, 1, self.grid_points)
        X, Y, Z = np.meshgrid(coords, coords, coords)
        
        # Initialize density field
        density_field = np.zeros((self.grid_points, self.grid_points, self.grid_points))
        
        # Compute electron density at each point
        for i in range(self.grid_points):
            for j in range(self.grid_points):
                for k in range(self.grid_points):
                    point = np.array([X[i,j,k], Y[i,j,k], Z[i,j,k]])
                    density_field[i,j,k] = self.compute_electron_density(point)
        
        # Normalize density field
        density_field = (density_field - np.min(density_field)) / (np.max(density_field) - np.min(density_field))
        
        return X, Y, Z, density_field

    def generate_grid_lines(self, X, Y, Z, density_field):
        """Generate grid lines with deformation based on density field."""
        lines = []
        colors = []
        
        # Create color scale based on density
        colorscale = colors.sequential.Viridis
        
        def get_color(density):
            return colors.sample_colorscale(colorscale, density)[0]
        
        # Generate lines along each axis
        for i in range(self.grid_points):
            for j in range(self.grid_points):
                # X-direction lines
                line_x = np.column_stack((X[:,i,j], Y[:,i,j], Z[:,i,j]))
                density_x = density_field[:,i,j]
                lines.append(line_x)
                colors.append([get_color(d) for d in density_x])
                
                # Y-direction lines
                line_y = np.column_stack((X[i,:,j], Y[i,:,j], Z[i,:,j]))
                density_y = density_field[i,:,j]
                lines.append(line_y)
                colors.append([get_color(d) for d in density_y])
                
                # Z-direction lines
                line_z = np.column_stack((X[i,j,:], Y[i,j,:], Z[i,j,:]))
                density_z = density_field[i,j,:]
                lines.append(line_z)
                colors.append([get_color(d) for d in density_z])
        
        return lines, colors

    def add_atom(self, position, atom_type):
        """Add an atom to the molecular structure."""
        self.atoms.append({
            'position': np.array(position),
            'type': atom_type
        })

    def visualize(self, show_atoms=True):
        """Create interactive 3D visualization with animated transitions."""
        # Compute deformed grid
        X, Y, Z, density_field = self.create_deformed_grid()
        lines, line_colors = self.generate_grid_lines(X, Y, Z, density_field)
        
        # Create figure
        fig = go.Figure()
        
        # Add grid lines with density-based coloring
        for line, colors in zip(lines, line_colors):
            fig.add_trace(go.Scatter3d(
                x=line[:,0], y=line[:,1], z=line[:,2],
                mode='lines',
                line=dict(
                    color=colors,
                    width=2
                ),
                showlegend=False
            ))
        
        # Add atoms if requested
        if show_atoms:
            atom_colors = {
                'H': '#FFFFFF',  # White
                'C': '#808080',  # Gray
                'N': '#0000FF',  # Blue
                'O': '#FF0000',  # Red
            }
            
            for atom in self.atoms:
                pos = atom['position']
                color = atom_colors.get(atom['type'], '#800080')  # Purple for unknown
                
                fig.add_trace(go.Scatter3d(
                    x=[pos[0]], y=[pos[1]], z=[pos[2]],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=color,
                        symbol='circle',
                        line=dict(
                            color='#FFFFFF',
                            width=1
                        )
                    ),
                    name=f"{atom['type']} atom"
                ))
        
        # Update layout with improved camera and lighting
        fig.update_layout(
            scene=dict(
                aspectmode='cube',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=2.0, y=2.0, z=2.0)
                ),
                xaxis=dict(range=[-1.2, 1.2], title='X'),
                yaxis=dict(range=[-1.2, 1.2], title='Y'),
                zaxis=dict(range=[-1.2, 1.2], title='Z'),
                dragmode='orbit'
            ),
            title=dict(
                text='Molecular Electron Density Visualization',
                y=0.95
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        fig.show()

# Example: Create water molecule
if __name__ == "__main__":
    mol_grid = RefinedMolecularGrid(resolution=12)
    
    # Define water molecule geometry
    # O-H bond length ≈ 0.96 Å, H-O-H angle ≈ 104.5°
    bond_length = 0.4  # Scaled for visualization
    angle = 104.5 * np.pi / 180
    
    # Add atoms
    mol_grid.add_atom((0.0, 0.0, 0.0), 'O')  # Oxygen at center
    mol_grid.add_atom((bond_length * np.sin(angle/2), bond_length * np.cos(angle/2), 0), 'H')
    mol_grid.add_atom((-bond_length * np.sin(angle/2), bond_length * np.cos(angle/2), 0), 'H')
    
    # Visualize
    mol_grid.visualize()