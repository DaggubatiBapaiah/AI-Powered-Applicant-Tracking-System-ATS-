import re
from typing import List, Set

def normalize_text(text: str) -> str:
    """
    Normalizes text by converting to lowercase, removing punctuation, 
    and removing extra spaces.
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text: str) -> List[str]:
    """
    Splits text into words.
    """
    return text.split()

def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Removes common English stopwords from a list of tokens.
    """
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
        'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
        'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
        'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
        'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing'
    }
    return [token for token in tokens if token not in stopwords]

def extract_keywords(text: str) -> Set[str]:
    """
    Full pipeline to extract unique keywords from text.
    """
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    cleaned_tokens = remove_stopwords(tokens)
    return set(cleaned_tokens)
