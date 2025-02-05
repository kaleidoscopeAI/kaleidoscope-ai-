# Shared Engine Implementation
class SharedEngine:
    def __init__(self, main_engine, mirrored_engine):
        self.main_engine = main_engine
        self.mirrored_engine = mirrored_engine

    def generate_final_insight(self):
        main_insight = self.main_engine.process_final_output()
        mirrored_insight = self.mirrored_engine.process_final_output()
        return main_insight + mirrored_insight
