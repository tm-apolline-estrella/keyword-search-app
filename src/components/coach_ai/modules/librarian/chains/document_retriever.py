# Import standard library modules
import re

# Import third-party library modules
from fuzzywuzzy import fuzz
from langchain_core.runnables import chain

# Import local modules
from src.components.coach_ai.helpers.cognitive_search import create_vector_store
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.librarian.constants import TOP_K
from src.components.coach_ai.settings import ModuleIndex

vectorstore = create_vector_store(ModuleIndex.LIBRARIAN.value)


# @chain
def retrieve_documents_from_vectorstore(input):
    question = str(input)

    search_results = vectorstore.semantic_hybrid_search_with_score_and_rerank(
        question, k=50
    )

    # Check if search_results is empty
    if not search_results:
        return []

    documents, scores, reranker_scores = map(list, zip(*search_results))
    for document, score, reranker_score in zip(documents, scores, reranker_scores):
        document.metadata["score"] = score
        document.metadata["reranker_score"] = reranker_score

    # print(documents[0].metadata.keys())
    return documents

@chain
def deduplicate_documents(documents, similarity_threshold=95):
    deduplicated_indices = []
    preprocessed_texts = [
        " ".join(re.sub(r"[^A-Za-z0-9\\s]", "", document.page_content).split())
        for document in documents
    ]
    for i in range(len(documents)):
        is_duplicate = False
        for j in deduplicated_indices:
            if i != j:  # To avoid comparing the element with itself
                text_1 = preprocessed_texts[i]
                text_2 = preprocessed_texts[j]
                similarity_score = fuzz.ratio(text_1, text_2)
                if similarity_score > similarity_threshold:
                    is_duplicate = True
                    break
        if not is_duplicate:
            deduplicated_indices.append(i)
    log.info(
        f"Deduplicated chunks: {len(deduplicated_indices)}", "api-document-retriever"
    )
    return [documents[i] for i in deduplicated_indices]


# TODO: Update to dynamic top-K
@chain
def get_top_k_documents(documents, k=TOP_K):
    documents = documents[:k]
    return documents


@chain
def get_additional_documents(input, top_n=2, neighbor_distance=1):
    documents = input["documents"]
    group_filter = input["group_filter"]

    documents = documents[:top_n]
    additional_documents = []
    log.debug(
        f"Getting {neighbor_distance*2} neighbor documents of the top {top_n}...",
        "api-document-retriever",
    )
    for idx, document in enumerate(documents):
        document_uuid = document.metadata["doc_uuid"]
        document_idx = int(document.metadata["doc_idx"])
        filters = f"""
            permitted_roles/any(g:search.in(g, '{group_filter}'))
            and doc_uuid eq '{document_uuid}'
            and doc_idx ne {document_idx}
            and doc_idx le {document_idx + neighbor_distance}
            and doc_idx ge {document_idx - neighbor_distance}
        """
        neighbor_documents = vectorstore.similarity_search(
            "", k=neighbor_distance * 2, filters=filters
        )
        neighbor_documents = sorted(
            neighbor_documents, key=lambda d: d.metadata["doc_idx"]
        )
        log.debug(
            f"Got {len(neighbor_documents)} neighbor documents for top {idx} chunk",
            "api-document-retriever",
        )
        additional_documents.extend(neighbor_documents)
    log.debug(
        f"Additional documents: {len(additional_documents)}", "api-document-retriever"
    )
    return additional_documents


@chain
def generate_context_from_documents(documents):
    context_list = [
        f"%%%%\nContent: {document.page_content}\nSource: {document.metadata['source']}\nPage: {document.metadata['page']}\n%%%%"
        for idx, document in enumerate(documents)
    ]
    formatted_context = "\n".join(context_list)
    return formatted_context


retrieve_source_documents = (
    retrieve_documents_from_vectorstore | deduplicate_documents | get_top_k_documents
)

retrieve_additional_documents = get_additional_documents
