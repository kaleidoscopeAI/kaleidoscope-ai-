class FeedbackIntegratedNode:
    def __init__(self, node_id, memory_threshold, kaleidoscope_engine):
        self.node_id = node_id
        self.memory_threshold = memory_threshold
        self.memory = []
        self.kaleidoscope_engine = kaleidoscope_engine

    def process_data(self, data):
        self.memory.append(data)
        if len(self.memory) >= self.memory_threshold:
            for memory_item in self.memory:
                self.kaleidoscope_engine.add_insight(memory_item)
            self.memory.clear()
