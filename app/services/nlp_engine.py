from sentence_transformers import SentenceTransformer
import spacy
from rank_bm25 import BM25Okapi
import nltk

# Download NLTK once
nltk.download('punkt', quiet=True)

print("Loading models... (This will happen only once)")

# Load BERT model ONCE
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load Spacy ONCE
nlp = spacy.load("en_core_web_sm")

print("Models loaded successfully!")
