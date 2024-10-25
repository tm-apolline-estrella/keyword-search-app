import streamlit as st

from src.components.traditional_keyword_search.app import traditional_keyword_search
from src.components.coach_ai.app import coach_ai_search

st.set_page_config(layout="wide")

with st.sidebar:
    st.subheader('Search engines')

    is_traditional_keyword_search_shown = st.checkbox("Keyword Search", value=True)
    is_coach_ai_shown = st.checkbox("CoachAI Search", value=True)

# Initialize session state variables if they don't exist
if 'query' not in st.session_state:
    st.session_state.query = ""

_, col2, _ = st.columns([1, 3, 1])

with col2:
    st.session_state.query = st.text_input("Query", key="user_query")

st.write("\n")
st.write("\n")
st.write("\n")

if is_traditional_keyword_search_shown and is_coach_ai_shown:
    col1, col2 = st.columns(2)

    with col1:
        container = st.container(border=True)
        with container:
            traditional_keyword_search(st.session_state.query)

    with col2:
        container = st.container(border=True)
        with container:
            coach_ai_search(st.session_state.query)
elif is_traditional_keyword_search_shown:
    container = st.container(border=True)
    with container:
        traditional_keyword_search(st.session_state.query)
elif is_coach_ai_shown:
    container = st.container(border=True)
    with container:
        coach_ai_search(st.session_state.query)
else:
    st.write('Please choose a search engine.')