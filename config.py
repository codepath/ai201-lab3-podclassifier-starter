import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Groq retired every Llama chat model in 2026. gpt-oss-120b is a Production-tier
# replacement. It reasons before it answers, and the reasoning tokens count
# against max_tokens. Leave max_tokens unset, or set it to 1000+, or pass
# reasoning_effort="low" (groq>=1.1.2). A tight cap returns an empty string.
LLM_MODEL = "openai/gpt-oss-120b"

# --- Classifier ---
VALID_LABELS = ["interview", "solo", "panel", "narrative"]

# --- Data ---
DATA_PATH = "./data"
TRAIN_FILE = "train_episodes.json"
TEST_FILE = "test_episodes.json"
LABELS_FILE = "my_labels.json"
