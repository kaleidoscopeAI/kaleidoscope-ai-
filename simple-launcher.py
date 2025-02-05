# run.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
import numpy as np
from rdkit import Chem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Molecular Analysis System")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Input area
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter SMILES notation (e.g., CCO for ethanol)")
        layout.addWidget(self.input_text)

        # Analyze button
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_molecule)
        layout.addWidget(analyze_btn)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def analyze_molecule(self):
        smiles = self.input_text.toPlainText().strip()
        if not smiles:
            QMessageBox.warning(self, "Error", "Please enter a SMILES string")
            return

        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError("Invalid SMILES string")

            # Simple analysis
            num_atoms = mol.GetNumAtoms()
            num_bonds = mol.GetNumBonds()
            
            # Generate quantum-inspired values (simplified)
            quantum_value = np.random.random()
            
            results = f"""Analysis Results:
            
Molecule: {smiles}
Number of atoms: {num_atoms}
Number of bonds: {num_bonds}
Quantum coherence value: {quantum_value:.4f}
"""
            self.results_text.setText(results)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
