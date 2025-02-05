# MemoryBank module
class MemoryBank:
    def __init__(self, id, capacity=100):
        self.id = id
        self.data = {}
        self.capacity = capacity

    def add_memory(self, key, value):
        if len(self.data) < self.capacity:
            self.data[key] = value
        else:
            print(f"MemoryBank {self.id} is full! Dumping data.")
            return self.dump_memory()

    def dump_memory(self):
        dumped_data = self.data.copy()
        self.data.clear()
        return dumped_data

    def is_full(self):
        return len(self.data) >= self.capacity
