# Import standard library modules
import re
from typing import List

# Import third-party library modules
from langchain.docstore.document import Document


def extract_latest_type(text):
    pattern = r"Category: (.+?)\n"
    matches = re.findall(pattern, text)
    if matches:
        return matches[-1]
    else:
        return None


def get_unique_doc_categories(documents: List[Document]):
    doc_categories = []
    for doc in documents:
        doc_category = extract_latest_type(doc.page_content)
        if doc_category not in doc_categories:
            doc_categories.append(doc_category)
    return doc_categories


def get_unique_sources(documents: List[Document]):
    sources = {doc.metadata.get("source") for doc in documents}
    return len(sources)


def sources_found_callback(doc_list, process_step_dict, key):
    if isinstance(doc_list, list):
        number_of_unique_sources = get_unique_sources(doc_list)
        doc_categories = get_unique_doc_categories(doc_list)
        process_step_dict[key] = {
            "source_count": number_of_unique_sources,
            "source_categories": doc_categories,
        }
