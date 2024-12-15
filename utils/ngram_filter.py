from typing import Set

def generate_ngrams(text: str, n: int = 2) -> Set[str]:
    """Generate n-grams from text.
    
    Args:
        text: Input text to generate n-grams from
        n: Length of each n-gram (default=2 for digrams)
        
    Returns:
        Set of n-grams
    """
    # Convert to lowercase and remove extra whitespace
    text = ' '.join(text.lower().split())
    
    # Generate n-grams including spaces
    ngrams = set()
    for i in range(len(text) - n + 1):
        ngrams.add(text[i:i + n])
    return ngrams

def text_matches_filter(filter_text: str, target_text: str, n: int = 2) -> bool:
    """Check if target text matches filter text using n-gram comparison.
    
    Args:
        filter_text: Text to filter by
        target_text: Text to check against filter
        n: Length of n-grams to use (default=2)
        
    Returns:
        True if target text matches filter criteria
    """
    if not filter_text or not target_text:
        return True
        
    # Generate n-grams for both texts
    filter_ngrams = generate_ngrams(filter_text, n)
    target_ngrams = generate_ngrams(target_text, n)
    
    # Check if any filter n-grams are present in target
    return any(ng in target_ngrams for ng in filter_ngrams)
