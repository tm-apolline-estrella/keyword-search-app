from src.helpers.search_algorithms import exact_keyword_search, tfidf_search, bm25_search

def search(query, pdf_texts, mode='bm25'):
    results = {}

    if mode == 'Exact match':
        results = exact_keyword_search(query, pdf_texts)
    
    if mode == 'TF-IDF':
        results = tfidf_search(query, pdf_texts)
        
    if mode == 'BM25':
        results = bm25_search(query, pdf_texts)

    return results
