import os
import re

import fitz
import streamlit as st

# from src.helpers.post_processing import get_highlighted_chunk
from src.helpers.loaders import get_original_text
from src.components.coach_ai.modules.librarian.chains.document_retriever import retrieve_documents_from_vectorstore

def coach_ai_search(query):
    # Function to go to previous page of search results
    def get_previous_page():
        if st.session_state.coach_ai_current_page > 0:
            st.session_state.coach_ai_current_page -= 1

    # Function to go to next page of search results
    def get_next_page():
        if st.session_state.coach_ai_current_page == total_page_count - 1:
            pass
        else:
            st.session_state.coach_ai_current_page += 1

    # @TODO: Implement highlighting of chunk in full text
    def get_pdf_text(file_name, page_num, base_folder_path="data"):
        pdf_file = ''

        for root, _, files in os.walk(base_folder_path):
            for local_file_name in files:
                if local_file_name.endswith(".pdf") and local_file_name == file_name:
                    pdf_file = os.path.join(root, local_file_name)
                    break
            if pdf_file != '': break

        # Open the PDF using PyMuPDF
        doc = fitz.open(pdf_file)
        text = ""

        page_num = page_num - 1
        page_count = 2

        for _ in range(page_count):
            if page_num < len(doc):
                page = doc.load_page(page_num)  # Load each page
                text += page.get_text()  # Extract text from the page
                page_num += 1

        # Close the document after extraction
        doc.close()

        return text
        
    # @TODO: Implement highlighting of chunk in full text
    @st.dialog("Full text")
    def view_full_text(full_text):
        st.write(full_text)

    ### Title
    st.title("CoachAI Search")

    # Initialize session state variables if they don't exist
    if query == '':
        st.write(':blue[Enter a query.]')

    # Perform the search based on the current query
    if query != '':
        search_results = retrieve_documents_from_vectorstore(query)
        total_search_result_count = len(search_results)

        # Get number of search results per page
        search_results_per_page = 15

        # Initialize session state for current page if not already done
        if 'coach_ai_current_page' not in st.session_state:
            st.session_state.coach_ai_current_page = 0

        total_page_count = (total_search_result_count + search_results_per_page - 1) // search_results_per_page

        start_index = st.session_state.coach_ai_current_page * search_results_per_page
        end_index = start_index + search_results_per_page

        ### Number of Search Results
        st.write(f":blue[{total_search_result_count} search results found.]")

        if len(search_results) > 0:
            search_result_id = 0
            for search_result in search_results[start_index:end_index]:
                file_name = os.path.basename(search_result.metadata['file_path'])
                page_num = search_result.metadata['page']
                chunk = search_result.metadata['captions']['text'].split("Key Hyperlinks:")[0]
                displayed_chunk = re.sub(r'^\s*#+\s*', '', chunk, flags=re.MULTILINE)
                displayed_chunk = displayed_chunk.replace('\n', '\n\n')
                
                # @TODO: Implement highlighting of chunk in full text
                # full_text = get_pdf_text(file_name, page_num)

                # print(search_result.metadata.keys())
                # print('file_name:', file_name)
                # print('page:', page_num)
                # print('full_text:', full_text)

                container = st.container(border=True)

                with container:
                    print("===============")
                    print(">", displayed_chunk)
                    print("===============")
                    print()

                    st.markdown(f"<h5 style='margin: 0;'>📄 {file_name}</h5>", unsafe_allow_html=True)
                    
                    # @TODO: Implement highlighting of chunk in full text
                    # if st.button("Full text", key=f"coach_ai_full_text_{search_result_id}"):
                    #     view_full_text(full_text)

                    st.markdown(f"... {displayed_chunk}", unsafe_allow_html=True)
                
                search_result_id += 1

        # Add buttons to go to previous or next page
        _, col1, col2, _ = st.columns([2, 1, 1, 2])

        ### Button to Previous Page
        with col1:
            back_disabled = st.session_state.coach_ai_current_page == 0
            if st.button(
                "⏮️ Back", 
                key="coach_ai_keyword_search_previous_page", on_click=get_previous_page, 
                disabled=back_disabled
                ):
                pass
        
        ### Button to Next Page
        with col2:
            next_disabled = st.session_state.coach_ai_current_page == total_page_count - 1
            if st.button(
                "Next ⏭️", 
                key="coach_ai_keyword_search_next_page", 
                on_click=get_next_page, 
                disabled=next_disabled
                ):
                pass