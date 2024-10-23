import re

from src.helpers.loaders import get_original_text

def get_highlighted_chunk(chunk, query_tokens):
    # text_lower = text.lower()
    # start_indices = [text_lower.find(token) for token in query_tokens if text_lower.find(token) != -1]
    
    # # If no exact matches found, return empty
    # if not start_indices:
    #     return text

    # # Get the first occurrence of any query token
    # start_idx = min(start_indices)
    # end_idx = start_idx + len(query_tokens[0])

    # # Define the context window around the first match
    # snippet_start = max(0, start_idx - window_size)
    # snippet_end = min(len(text_lower), end_idx + window_size)
    # print(snippet_start, snippet_end)

    # # Extract snippet and highlight keywords
    # snippet = text[snippet_start:snippet_end]
    # for token in query_tokens:
    #     snippet = re.sub(token, lambda match: colored(match.group(0), 'red'), snippet, flags=re.IGNORECASE)

    chunk_tokens = get_original_text(chunk)

    highlighted_chunk = chunk

    for query_token in query_tokens:
        for chunk_token in chunk_tokens:
            if (query_token.lower() == chunk_token.lower()) or (query_token.lower() in chunk_token.lower()):
                print(query_token, chunk_token)
                highlighted_chunk = chunk.replace(
                    chunk_token, 
                    f"<span style='color:red;'><strong>{chunk_token}</strong></span>"
                    )

    return highlighted_chunk

    # return snippet