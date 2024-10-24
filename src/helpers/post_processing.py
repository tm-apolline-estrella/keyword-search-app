import re


from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from src.helpers.loaders import get_original_text

def get_highlighted_chunk(chunk, query_tokens):
    chunk_tokens = get_original_text(chunk)

    highlighted_chunk = chunk

    query_tokens = [query_token for query_token in query_tokens if query_token not in ENGLISH_STOP_WORDS]

    for query_token in query_tokens:
        for chunk_token in chunk_tokens:
            if (query_token.lower() == chunk_token.lower()) or (query_token.lower() in chunk_token.lower()):
                print(query_token, chunk_token)
                highlighted_chunk = re.sub(
                    r'\b' + re.escape(chunk_token) + r'\b', 
                    f"<span style='color:red;'><strong>{chunk_token}</strong></span>",
                    chunk
                )

    return highlighted_chunk

    # return snippet