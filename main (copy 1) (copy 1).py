import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from core.kaleidoscope_engine import KaleidoscopeEngine
from core.feedback_node import FeedbackIntegratedNode
from utils.visualizer import Visualizer
from utils.addiction_module import AddictionModule

class KaleidoscopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kaleidoscope AI")
        self.root.geometry("800x600")

        self.engine = KaleidoscopeEngine()
        self.addiction_module = AddictionModule()
        self.main_files = []
        self.mirrored_files = []

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Kaleidoscope AI", font=("Helvetica", 24))
        title_label.pack(pady=10)

        # Main Dataset Upload
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        main_label = tk.Label(main_frame, text="Upload Main Dataset:")
        main_label.pack(side=tk.LEFT, padx=5)

        main_button = tk.Button(main_frame, text="Upload Files", command=self.upload_main)
        main_button.pack(side=tk.LEFT, padx=5)

        # Mirrored Dataset Upload
        mirrored_frame = tk.Frame(self.root)
        mirrored_frame.pack(pady=10)

        mirrored_label = tk.Label(mirrored_frame, text="Upload Mirrored Dataset:")
        mirrored_label.pack(side=tk.LEFT, padx=5)

        mirrored_button = tk.Button(mirrored_frame, text="Upload Files", command=self.upload_mirrored)
        mirrored_button.pack(side=tk.LEFT, padx=5)

        # Start Button
        start_button = tk.Button(self.root, text="Start Processing", font=("Helvetica", 14), command=self.start_processing)
        start_button.pack(pady=20)

        # Status Display
        self.status_text = tk.Text(self.root, height=15, width=90, state=tk.DISABLED)
        self.status_text.pack(pady=10)

    def upload_main(self):
        files = filedialog.askopenfilenames(title="Select Main Dataset Files")
        self.main_files.extend(files)
        self.update_status(f"Main dataset files uploaded: {files}")

    def upload_mirrored(self):
        files = filedialog.askopenfilenames(title="Select Mirrored Dataset Files")
        self.mirrored_files.extend(files)
        self.update_status(f"Mirrored dataset files uploaded: {files}")

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.config(state=tk.DISABLED)
        self.status_text.see(tk.END)

    def start_processing(self):
        if not self.main_files or not self.mirrored_files:
            messagebox.showerror("Error", "Please upload both main and mirrored datasets.")
            return

        self.update_status("Starting processing...")
        threading.Thread(target=self.process_data).start()

    def process_data(self):
        try:
            # Parse and process main dataset
            for file in self.main_files:
                data = self.addiction_module.parse_data(file)
                node = FeedbackIntegratedNode("main_node", memory_threshold=5, mirrored_network=None, kaleidoscope_engine=self.engine)
                node.process_data(str(data))
                self.update_status(f"Processed main dataset file: {file}")

            # Parse and process mirrored dataset
            for file in self.mirrored_files:
                data = self.addiction_module.parse_data(file)
                node = FeedbackIntegratedNode("mirrored_node", memory_threshold=5, mirrored_network=None, kaleidoscope_engine=self.engine)
                node.process_data(str(data))
                self.update_status(f"Processed mirrored dataset file: {file}")

            # Generate and display final insights
            final_output = self.engine.process_final_output()
            self.update_status(f"Final Insight: {final_output}")
        except Exception as e:
            self.update_status(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KaleidoscopeApp(root)
    root.mainloop()
