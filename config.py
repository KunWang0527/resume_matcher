# Holds API key, model paths, thresholds
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Default GPT model used by GPT parser; adjust as needed
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

# Model Paths
MODEL_DIR = Path(__file__).parent / "models"
# Full Sentence-Transformers model identifier
SENTENCE_BERT_MODEL = os.getenv("SENTENCE_BERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Data Paths
DATA_DIR = Path(__file__).parent / "data"
RESUMES_FILE = DATA_DIR / "resumes.json"
LABELED_EVAL_FILE = DATA_DIR / "labeled_eval.json"

# Scoring Thresholds
SIMILARITY_THRESHOLD = 0.7
# Weights for hybrid semantic similarity (BERT + TF-IDF)
SEMANTIC_BERT_WEIGHT = 0.7
SEMANTIC_TFIDF_WEIGHT = 0.3

# Rule-based component weights and caps
RULE_WEIGHTS = {
    "required_skill_point": 10,      # per matched required skill
    "preferred_skill_point": 3,      # per matched preferred skill
    "experience_title_point": 5,     # per experience title match
    "experience_desc_bonus": 1,      # per required skill found in experience description
    "experience_desc_bonus_cap": 10, # cap total description bonus
    "education_full": 10,            # full education match
    "education_partial": 5,          # partial/related field match
    "projects_cap": 10,              # cap for projects contribution
    "company_point": 8,              # per preferred company occurrence
    "company_cap": 20                # cap for company contribution
}

# Penalty applied if must-have skills are missing
MUST_HAVE_PENALTY = 30


# Processing Settings
MAX_RESUME_LENGTH = 10000
BATCH_SIZE = 32