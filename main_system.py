
import logging
from chatbot.kaleidoscope_chatbot import KaleidoscopeChatbot
from system_simulation import SystemSimulation

logging.basicConfig(
    filename="main_system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class MainSystem:
    def __init__(self):
        self.chatbot = KaleidoscopeChatbot()
        self.simulation = SystemSimulation()

    def initialize(self):
        self.chatbot.initialize()
        logging.info("Main system initialized.")

    def interact(self):
        print("Type 'exit' to quit or 'simulate <type>' to trigger simulations.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            elif user_input.startswith("simulate"):
                simulation_type = user_input.split(" ", 1)[1]
                self.simulation.run([f"{simulation_type}_data.csv"])
            else:
                response = self.chatbot.get_response(user_input)
                print(f"Chatbot: {response}")

    def shutdown(self):
        logging.info("System shut down.")

if __name__ == "__main__":
    system = MainSystem()
    try:
        system.initialize()
        system.interact()
    finally:
        system.shutdown()
