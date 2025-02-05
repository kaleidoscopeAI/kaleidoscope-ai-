# SharedEngine module
import hashlib

class SharedEngine:
    def __init__(self, mirrored_network, main_network):
        self.mirrored_network = mirrored_network
        self.main_network = main_network

    def generate_final_insight(self):
        mirrored_data = self.mirrored_network.get_data()
        main_data = self.main_network.get_data()
        combined = mirrored_data + main_data
        return hashlib.sha256(combined).digest()
