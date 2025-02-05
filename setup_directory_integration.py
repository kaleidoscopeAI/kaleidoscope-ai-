import os
import json

def create_dataset_directory_script(modules_path):
    """
    Create DatasetDirectory.py in the specified modules path.
    """
    script_content = """
import os

class DatasetDirectory:
    \"\"\"Centralized manager for all dataset paths.\"\"\"

    def __init__(self):
        # Define dataset categories and mappings
        self.dataset_map = {
            "drugs": {
                "Drug1": "data/drug/erlotinib.sdf",
                "Drug2": "data/drug/gefitinib.sdf",
                "DrugData": "data/drug_data.csv",
                "DrugResponse": "data/drug_response.csv"
            },
            "proteins": {
                "Protein1": "data/protein/alk_kinase.pdb",
                "Protein2": "data/protein/pd1_pdl1.pdb",
                "Protein3": "data/protein/ros1_kinase.pdb"
            },
            "genomics": {
                "Genomic1": "data/genomic/cosmic_mutations.tsv.gz",
                "Genomic2": "data/gene/GDS6248.soft.gz"
            },
            "clinical_trials": {
                "Trial1": "data/clinical_trials/wget-log",
                "Trial2": "data/clinical/clinvar.vcf.gz"
            },
            "immune": {
                "Immune1": "data/immune_data/pd1_structure.pdb"
            },
            "pathways": {
                "Pathway1": "data/pathway/9606.protein.links.detailed.v11.5.txt.gz",
                "Pathway2": "data/lung_cancer_pathway.xml"
            }
        }

    def get_path(self, category, key):
        \"\"\"
        Retrieve the file path for a given dataset key in a category.

        Args:
            category (str): The dataset category (e.g., 'drugs').
            key (str): The dataset identifier (e.g., 'Drug1').

        Returns:
            str: The dataset path if found, otherwise None.
        \"\"\"
        category_map = self.dataset_map.get(category)
        if not category_map:
            print(f"Warning: Category '{category}' not found.")
            return None
        path = category_map.get(key)
        if path and os.path.exists(path):
            return path
        else:
            print(f"Warning: Dataset '{key}' in category '{category}' not found or path does not exist.")
            return None

    def list_datasets(self, category=None):
        \"\"\"
        List datasets in a category or all categories.

        Args:
            category (str, optional): The dataset category.

        Returns:
            dict or list: Datasets in the category or all datasets.
        \"\"\"
        if category:
            return self.dataset_map.get(category, {})
        return self.dataset_map
    """
    dataset_dir_path = os.path.join(modules_path, "DatasetDirectory.py")
    with open(dataset_dir_path, "w") as f:
        f.write(script_content)
    print(f"DatasetDirectory.py created at {dataset_dir_path}")


def create_datasets_json(data_path):
    """
    Create datasets.json in the data directory for future scalability.
    """
    datasets = {
        "drugs": {
            "Drug1": "data/drug/erlotinib.sdf",
            "Drug2": "data/drug/gefitinib.sdf",
        },
        "proteins": {
            "Protein1": "data/protein/alk_kinase.pdb",
            "Protein2": "data/protein/pd1_pdl1.pdb",
        }
    }

    json_path = os.path.join(data_path, "datasets.json")
    with open(json_path, "w") as f:
        json.dump(datasets, f, indent=4)
    print(f"datasets.json created at {json_path}")


def integrate_into_main(project_root):
    """
    Update main.py to use the DatasetDirectory for dataset lookups.
    """
    main_path = os.path.join(project_root, "main.py")
    if not os.path.exists(main_path):
        print("main.py not found. Skipping integration.")
        return

    new_main_content = """
import ray
from modules.DatasetDirectory import DatasetDirectory
from core.NodeManager import NodeManager
from modules.SimulationManager import SimulationManager

if __name__ == "__main__":
    ray.init()

    # Initialize directory manager
    directory = DatasetDirectory()

    # Lookup datasets dynamically
    drug_path = directory.get_path("drugs", "Drug1")
    protein_path = directory.get_path("proteins", "Protein1")

    if not drug_path or not protein_path:
        print("Required datasets are missing. Please verify paths.")
        exit()

    # Initialize components
    manager = NodeManager.remote()
    simulation_manager = SimulationManager()

    # Add nodes and run simulations
    node1 = manager.add_node("Node1", "Exploration", {"Drug1": drug_path, "Protein1": protein_path})
    ray.get(manager.distribute_work.remote())

    docking_results = simulation_manager.run_simulations(["Drug1"], ["Protein1"])
    print("Docking Results:", docking_results)
    """
    with open(main_path, "w") as f:
        f.write(new_main_content)
    print(f"main.py updated at {main_path}")


if __name__ == "__main__":
    # Define paths based on your project structure
    project_root = "/home/gym/Unified_AI_Core_Deployment_8"
    modules_path = os.path.join(project_root, "modules")
    data_path = os.path.join(project_root, "data")

    # Create DatasetDirectory.py
    create_dataset_directory_script(modules_path)

    # Create datasets.json
    create_datasets_json(data_path)

    # Integrate DatasetDirectory into main.py
    integrate_into_main(project_root)

    print("Directory integration setup complete.")
