import streamlit as st

from src.helpers.loaders import get_pdf_texts, get_preprocessed_text
from src.helpers.post_processing import get_highlighted_chunk
from src.helpers.search import search

def traditional_keyword_search(query):
    # Function to go to previous page of search results
    def get_previous_page():
        if st.session_state.traditional_keyword_search_current_page > 0:
            st.session_state.traditional_keyword_search_current_page -= 1

    # Function to go to next page of search results
    def get_next_page():
        if st.session_state.traditional_keyword_search_current_page == total_page_count - 1:
            pass
        else:
            st.session_state.traditional_keyword_search_current_page += 1

    # Check if PDF texts are already loaded in session state
    if 'pdf_texts' not in st.session_state:
        # Load PDFs only once and store in session state
        base_folder_path = "./data"
        st.session_state.pdf_texts = get_pdf_texts(base_folder_path)

    # Initialize session state variables if they don't exist
    if 'search_algorithm' not in st.session_state:
        st.session_state.search_algorithm = "BM25"  # Default algorithm

    col1, _, col3 = st.columns([2.5, 0.5, 1.25])

    ### Title
    with col1:
        st.title("Keyword Search")

    ### Search Algorithm Select Box
    with col3:
        # Update the session state for query
        st.session_state.search_algorithm = st.selectbox(
            "Search algorithm",
            ("Exact match", "TF-IDF", "BM25"),
            key="traditional_keyword_search_user_search_algorithm",
            index=2,
            # on_change=perform_search
            )
        
    # Initialize session state variables if they don't exist
    if query == '':
        st.write(':blue[Enter a query.]')

    with st.spinner(":blue[Generating search results...]"):
        if query != '':
            # Perform the search based on the current query and algorithm
            search_results = search(query, st.session_state.pdf_texts, mode=st.session_state.search_algorithm)
            total_search_result_count = len(search_results)

            # Get number of search results per page
            search_results_per_page = 15

            # Initialize session state for current page if not already done
            if 'traditional_keyword_search_current_page' not in st.session_state:
                st.session_state.traditional_keyword_search_current_page = 0

            total_page_count = (total_search_result_count + search_results_per_page - 1) // search_results_per_page

            start_index = st.session_state.traditional_keyword_search_current_page * search_results_per_page
            end_index = start_index + search_results_per_page

            ### Number of Search Results
            st.write(f":blue[{total_search_result_count} search results found.]")

            if search_results != {}:
                displayed_search_results = list(search_results.items())
                
                ### Search Results
                for file_name, details in displayed_search_results[start_index:end_index]:
                    chunk = details['chunk']
                    query_tokens = get_preprocessed_text(query)

                    highlighted_chunk = get_highlighted_chunk(chunk, query_tokens)

                    container = st.container(border=True)

                    with container:
                        st.markdown(f"<h5 style='margin: 0;'>📄 {file_name}</h5>", unsafe_allow_html=True)
                        st.markdown(f"... {highlighted_chunk}...", unsafe_allow_html=True)

            # Add buttons to go to previous or next page
            _, col1, col2, _ = st.columns([2, 1, 1, 2])

            ### Button to Previous Page
            with col1:
                back_disabled = st.session_state.traditional_keyword_search_current_page == 0
                if st.button(
                    "⏮️ Back", 
                    key="traditional_keyword_search_previous_page", on_click=get_previous_page, 
                    disabled=back_disabled
                    ):
                    pass
            
            ### Button to Next Page
            with col2:
                next_disabled = st.session_state.traditional_keyword_search_current_page == total_page_count - 1
                if st.button(
                    "Next ⏭️", 
                    key="traditional_keyword_search_next_page", 
                    on_click=get_next_page, 
                    disabled=next_disabled
                    ):
                    pass

        # st.write(search_results)