import re

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

def is_agricultural_query(text: str) -> bool:
    """
    Checks if the text contains any agricultural or regional vocabulary terms.
    """
    cleaned = clean_text(text)
    words = cleaned.split()
    
    # Vocabulary terms drawn from generate_dataset.py
    agri_keywords = {
        # Crops
        "wheat", "wheet", "gehu", "gehun", "kanak", "rice", "rise", "dhan", "chawal", 
        "corn", "makka", "cotton", "kapas", "sugarcane", "ganna", "mustard", "sarso", 
        "potato", "aloo", "onion", "pyaz", "tomato", "tamatar", "soybean", "soyabean",
        # Market
        "price", "pryce", "rate", "ret", "bhav", "baav", "paise", "prise", "mkt", "market", "mandi", "markit",
        # Weather
        "weather", "wether", "mosam", "mausam", "wedder", "rain", "barish", "baarish", "temp", "dhoop", "heat",
        # Disease
        "disease", "sick", "bimari", "keeda", "pest", "bugs", "yellowing", "spots", "dying", "sukha", "dry",
        "leaves", "pattiyan", "root", "jad", "stem", "tana", "crop", "fasal",
        # Advice
        "fertilizer", "khad", "urea", "dap", "water", "pani", "seeds", "beej", "plant", "boi", "grow", "ugana",
        # Subsidy
        "subsidy", "sabsidi", "scheme", "schem", "yojana", "loan", "karz", "govt", "sarkar", "pm", "kisan", "bank"
    }
    
    return any(w in agri_keywords for w in words)

