import streamlit as st

from src.helpers.loaders import get_pdf_texts, get_preprocessed_text
from src.helpers.post_processing import get_highlighted_chunk
from src.helpers.search import search

import streamlit as st

# Custom CSS to change the border color to blue when focused
custom_css = """
<style>
/* Change input box border color when focused */
stTextInput input:focus {
    border-color: blue !important;
}

/* Change select box border color when focused */
stSelectbox select:focus {
    border-color: blue !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Function to perform the search and update the results
def perform_search():
    if st.session_state.query:  # Only search if there is a query
        st.session_state.search_algorithm = st.session_state.user_search_algorithm
        st.session_state.query = st.session_state.user_query

# Function to go to previous page of search results
def get_previous_page():
    if st.session_state.current_page > 0:
        st.session_state.current_page -= 1

# Function to go to next page of search results
def get_next_page():
    if st.session_state.current_page == total_page_count - 1:
        pass
    else:
        st.session_state.current_page += 1

st.title("Keyword Search")

# Check if PDF texts are already loaded in session state
if 'pdf_texts' not in st.session_state:
    # Load PDFs only once and store in session state
    base_folder_path = "./data"
    st.session_state.pdf_texts = get_pdf_texts(base_folder_path)

# Initialize session state variables if they don't exist
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'search_algorithm' not in st.session_state:
    st.session_state.search_algorithm = "BM25"  # Default algorithm

col1, col2 = st.columns([1, 3])

with col1:
    # Update the session state for search algorithm
    st.session_state.search_algorithm = st.selectbox(
        "Search algorithm",
        ("Exact match", "TF-IDF", "BM25"),
        key="user_search_algorithm",
        index=2,
        on_change=perform_search
        )

with col2:
    # Update the session state for query
    st.session_state.query = st.text_input("Query", key="user_query", on_change=perform_search)

# Perform the search based on the current query and algorithm
search_results = search(st.session_state.query, st.session_state.pdf_texts, mode=st.session_state.search_algorithm)
total_search_result_count = len(search_results)

# Get number of search results per page
search_results_per_page = 15

# Initialize session state for current page if not already done
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

total_page_count = (total_search_result_count + search_results_per_page - 1) // search_results_per_page

start_index = st.session_state.current_page * search_results_per_page
end_index = start_index + search_results_per_page

st.write(f":blue[{total_search_result_count} search results found.]")

if search_results != {}:
    displayed_search_results = list(search_results.items())
    
    # Apply slicing to get the desired chunk of results
    for file_name, details in displayed_search_results[start_index:end_index]:
        chunk = details['chunk']
        query_tokens = get_preprocessed_text(st.session_state.query)

        highlighted_chunk = get_highlighted_chunk(chunk, query_tokens)

        container = st.container(border=True)

        with container:
            # st.subheader(file_name)
            st.markdown(f"<h5 style='margin: 0;'>📄 {file_name}</h5>", unsafe_allow_html=True)
            # container.write(highlighted_chunk)
            st.markdown(f"... {highlighted_chunk}...", unsafe_allow_html=True)

# Add buttons to go to previous or next page
_, col1, col2, _ = st.columns([2, 1, 1, 2])

with col1:
    back_disabled = st.session_state.current_page == 0
    if st.button("⏮️ Back", on_click=get_previous_page, disabled=back_disabled):
        pass

with col2:
    next_disabled = st.session_state.current_page == total_page_count - 1
    if st.button("Next ⏭️", on_click=get_next_page, disabled=next_disabled):
        pass

# st.write(search_results)
# print()