# KaleidoscopeEngine module
import hashlib
import struct
from typing import List, Dict, Any

class KaleidoscopeEngine:
    def __init__(self, num_gears=20, gear_memory_threshold=10):
        self.memory_banks = [[] for _ in range(num_gears)]
        self.gear_memory_threshold = gear_memory_threshold
        self.current_gear = 0

    def add_insight(self, insight: bytes):
        if len(self.memory_banks[self.current_gear]) < self.gear_memory_threshold:
            self.memory_banks[self.current_gear].append(insight)
        else:
            self.spin_kaleidoscope()
            self.memory_banks[self.current_gear].append(insight)

    def spin_kaleidoscope(self):
        for i in range(len(self.memory_banks) - 1):
            overflow = self.memory_banks[i][self.gear_memory_threshold // 2:]
            self.memory_banks[i] = self.memory_banks[i][:self.gear_memory_threshold // 2]
            self.memory_banks[i + 1].extend(overflow)
        self.current_gear = (self.current_gear + 1) % len(self.memory_banks)

    def process(self) -> bytes:
        combined_data = b''.join(item for bank in self.memory_banks for item in bank)
        return hashlib.sha256(combined_data).digest()

    def decode_final_insight(self, binary_data: bytes) -> dict:
        meta_len = struct.unpack('!I', binary_data[:4])[0]
        metadata = binary_data[4:4 + meta_len].decode('utf-8')
        data_len = struct.unpack('!I', binary_data[4 + meta_len:8 + meta_len])[0]
        data = binary_data[8 + meta_len:8 + meta_len + data_len]
        return {
            "metadata": eval(metadata),
            "data": data.decode('utf-8')
        }

    def process_final_output(self) -> str:
        final_binary = self.process()
        decoded = self.decode_final_insight(final_binary)
        return f"Insight: {decoded['data']} (Metadata: {decoded['metadata']})"

    def status(self) -> Dict[str, Any]:
        return {
            "current_gear": self.current_gear,
            "memory_bank_states": [len(bank) for bank in self.memory_banks]
        }
