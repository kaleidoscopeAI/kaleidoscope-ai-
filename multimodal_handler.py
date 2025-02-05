import base64
from rdkit import Chem
from rdkit.Chem import Descriptors
from PIL import Image

def handle_text_data(text):
    """Processes text data."""
    return text.lower().strip()

def handle_image_data(image_path):
    """Processes image data (e.g., converting to base64)."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def handle_molecular_data(smiles):
    """Processes molecular data."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None
    return {
        "MolecularWeight": Descriptors.MolWt(mol),
        "LogP": Descriptors.MolLogP(mol),
        "NumAtoms": mol.GetNumAtoms()
    }

# Example Usage
if __name__ == "__main__":
    print(handle_text_data(" Example Text "))
    print(handle_image_data("example_image.png"))
    print(handle_molecular_data("CCO"))
