import re
import numpy as np

def clean_text(text: str) -> str:
    """
    Cleans incoming SMS text:
    1. Converts to lowercase.
    2. Keeps only letters, numbers, and spaces (preserving agricultural numeric details).
    3. Strips extra whitespace.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return " ".join(text.split())

def get_sentence_vector(text: str, model) -> np.ndarray:
    """
    Cleans text and calculates the average word vector of the tokens.
    Accepts either a Gensim model (Word2Vec/FastText) or model.wv (KeyedVectors).
    """
    model_wv = model.wv if hasattr(model, 'wv') else model
    cleaned = clean_text(text)
    words = cleaned.split()
    vectors = [model_wv[w] for w in words if w in model_wv]
    if not vectors:
        return np.zeros(model_wv.vector_size)
    return np.mean(vectors, axis=0)
