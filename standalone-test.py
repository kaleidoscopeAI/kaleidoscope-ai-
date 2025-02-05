import urllib.request
import json
from datetime import datetime
import numpy as np
from typing import Dict, List, Any

# Simplified test components
class MemoryBank:
    def __init__(self):
        self.insights = []
        
    def add_insight(self, insight):
        self.insights.append(insight)
        
    def get_insights(self):
        return self.insights

class TestEngine:
    def __init__(self):
        self.memory_bank = MemoryBank()
        
    def process_protein(self, protein_data):
        # Extract key information
        processed = {
            'id': protein_data['primaryAccession'],
            'name': protein_data.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
            'functions': [c['value'] for c in protein_data.get('comments', []) if c['commentType'] == 'FUNCTION'],
            'locations': [c['value'] for c in protein_data.get('comments', []) if c['commentType'] == 'SUBCELLULAR LOCATION']
        }
        
        self.memory_bank.add_insight(processed)
        return processed

print("Starting Live Test...")
engine = TestEngine()

# Fetch real protein data
url = "https://rest.uniprot.org/uniprotkb/search?query=locations:(location:membrane)&format=json"
print("Fetching membrane protein data...")

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())
    proteins = data['results']
    print(f"Processing {len(proteins)} membrane proteins...")
    
    for protein in proteins:
        result = engine.process_protein(protein)
        print(f"Processed: {result['name']}")

print("\nAnalysis Complete")
insights = engine.memory_bank.get_insights()
print(f"Total Proteins Processed: {len(insights)}")

# Display sample insights
print("\nSample Protein Analysis:")
for insight in insights[:3]:
    print(f"\nProtein: {insight['name']}")
    print(f"Functions: {', '.join(insight['functions'])}")
    print(f"Locations: {', '.join(insight['locations'])}")
