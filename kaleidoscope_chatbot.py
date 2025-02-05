
import logging
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Configure logging
logging.basicConfig(
    filename="chatbot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class KaleidoscopeChatbot:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.chat_history_ids = None
        self.chatterbot = ChatBot(
            "KaleidoscopeAI",
            storage_adapter="chatterbot.storage.SQLStorageAdapter",
            logic_adapters=[
                "chatterbot.logic.MathematicalEvaluation",
                "chatterbot.logic.BestMatch"
            ],
            database_uri="sqlite:///chatbot_database.sqlite3"
        )
        self.trainer = ListTrainer(self.chatterbot)

    def initialize(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        logging.info("Chatbot initialized successfully.")

    def train_chatterbot(self, conversations):
        try:
            self.trainer.train(conversations)
            logging.info("ChatterBot successfully trained.")
        except Exception as e:
            logging.error(f"Error training ChatterBot: {e}")

    def get_response(self, user_input: str) -> str:
        try:
            input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors="pt")
            bot_input_ids = torch.cat([self.chat_history_ids, input_ids], dim=-1) if self.chat_history_ids else input_ids
            self.chat_history_ids = self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
            response = self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            logging.info(f"DialoGPT response: {response}")
            return response
        except Exception:
            response = self.chatterbot.get_response(user_input)
            logging.info(f"ChatterBot response: {response}")
            return str(response)
