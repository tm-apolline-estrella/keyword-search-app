import numpy as np

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

from src.helpers.loaders import get_original_text, get_preprocessed_text

# Function to perform exact keyword search and return text snippets
def exact_keyword_search(query, pdf_texts):
    original_texts = {file_name: get_original_text(text) for file_name, text in pdf_texts.items()}
    preprocessed_texts = {file_name: get_preprocessed_text(text) for file_name, text in pdf_texts.items()}
    query_tokens = get_preprocessed_text(query)

    results = {}
    
    for file_name, tokens in preprocessed_texts.items():
        # Find exact match
        if all(token in tokens for token in query_tokens):
            # Rebuild text to get the snippet
            original_text = original_texts[file_name]
            text = ' '.join(original_text)
            start_idx = text.lower().find(query.lower())
            snippet = text[max(0, start_idx-100): start_idx+300]  # Show surrounding text
            results[file_name] = {
                'chunk' : snippet,
                'score' : 1
            }
    
    results = dict(sorted(results.items(), key=lambda item: item[1]['score'], reverse=True))
    results = {key: value for key, value in results.items() if value['chunk'] != ''}
    
    return results

# Function to perform TF-IDF search and return text snippets
def tfidf_search(query, pdf_texts, threshold=0.05):
    original_texts = {file_name: get_original_text(text) for file_name, text in pdf_texts.items()}
    preprocessed_texts = {file_name: get_preprocessed_text(text) for file_name, text in pdf_texts.items()}

    preprocessed_documents = [' '.join(text) for text in preprocessed_texts.values()]
    original_documents = [' '.join(text) for text in original_texts.values()]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_documents)
    query_vector = vectorizer.transform([query])
    
    similarity_scores = (tfidf_matrix * query_vector.T).toarray()
    
    results = {}
    for i, score in enumerate(similarity_scores):
        if np.max(score) > 0:  # If there's a relevant score
            file_name = list(preprocessed_texts.keys())[i]
            text = original_documents[i]
            start_idx = text.lower().find(query.lower())
            snippet = text[max(0, start_idx-100): start_idx+300]
            score = score[0]
            results[file_name] = {
                'chunk' : snippet,
                'score' : score
            }

    results = dict(sorted(results.items(), key=lambda item: item[1]['score'], reverse=True))
    results = {key: value for key, value in results.items() if value['chunk'] != ''}
    results = {key: value for key, value in results.items() if value['score'] >= threshold and value['chunk'] != ''}

    return results

# Function to perform BM25 search and return text snippets
def bm25_search(query, pdf_texts, threshold=1.75):
    original_texts = {file_name: get_original_text(text) for file_name, text in pdf_texts.items()}
    preprocessed_texts = {file_name: get_preprocessed_text(text) for file_name, text in pdf_texts.items()}

    bm25 = BM25Okapi(list(preprocessed_texts.values()))
    query_tokens = get_preprocessed_text(query)
    scores = bm25.get_scores(query_tokens)

    results = {}
    for i, score in enumerate(scores):
        if score > 0:  # If there's a relevant score
            file_name = list(preprocessed_texts.keys())[i]
            text = ' '.join(original_texts[file_name])
            start_idx = text.lower().find(query.lower())
            # print(start_idx)
            snippet = text[max(0, start_idx-100): start_idx+300]
            results[file_name] = {
                'chunk' : snippet,
                'score' : score
            }

    results = dict(sorted(results.items(), key=lambda item: item[1]['score'], reverse=True))
    results = {key: value for key, value in results.items() if value['chunk'] != ''}
    results = {key: value for key, value in results.items() if value['score'] >= threshold and value['chunk'] != ''}

    return results

