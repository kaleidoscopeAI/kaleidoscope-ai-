import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from core.kaleidoscope_engine import KaleidoscopeEngine
from core.feedback_node import FeedbackIntegratedNode
from core.shared_engine import SharedEngine
from utils.visualizer import Visualizer
from utils.addiction_module import AddictionModule
from utils.binary_processor import BinaryProcessor

class KaleidoscopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kaleidoscope AI")
        self.root.geometry("1200x900")
        self.engine = KaleidoscopeEngine()
        self.shared_engine = SharedEngine(self.engine, self.engine)
        self.addiction_module = AddictionModule()
        self.binary_processor = BinaryProcessor()
        self.main_files = []
        self.mirrored_files = []
        self.visualizer = Visualizer(self.engine)
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Kaleidoscope AI", font=("Helvetica", 24))
        title_label.pack(pady=10)
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)
        tk.Label(main_frame, text="Upload Main Dataset:").pack(side=tk.LEFT, padx=5)
        tk.Button(main_frame, text="Upload Files", command=self.upload_main).pack(side=tk.LEFT, padx=5)
        mirrored_frame = tk.Frame(self.root)
        mirrored_frame.pack(pady=10)
        tk.Label(mirrored_frame, text="Upload Mirrored Dataset:").pack(side=tk.LEFT, padx=5)
        tk.Button(mirrored_frame, text="Upload Files", command=self.upload_mirrored).pack(side=tk.LEFT, padx=5)
        tk.Button(self.root, text="Start Processing", command=self.start_processing).pack(pady=20)
        tk.Button(self.root, text="Visualize System", command=self.visualize_system).pack(pady=10)
        self.status_text = tk.Text(self.root, height=20, width=110, state=tk.DISABLED)
        self.status_text.pack(pady=10)

    def upload_main(self):
        files = filedialog.askopenfilenames(title="Select Main Dataset Files")
        self.main_files.extend(files)

    def upload_mirrored(self):
        files = filedialog.askopenfilenames(title="Select Mirrored Dataset Files")
        self.mirrored_files.extend(files)

    def start_processing(self):
        threading.Thread(target=self.process_data).start()

    def process_data(self):
        pass

    def visualize_system(self):
        self.visualizer.visualize_gears()
        self.visualizer.visualize_memory()

if __name__ == "__main__":
    root = tk.Tk()
    app = KaleidoscopeApp(root)
    root.mainloop()
