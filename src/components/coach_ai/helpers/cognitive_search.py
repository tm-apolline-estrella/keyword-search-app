# Import standard library modules
from typing import List

# Import third-party library modules
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from langchain_community.vectorstores import azuresearch

# Import local modules
import src.components.coach_ai.settings as settings
from src.components.coach_ai.helpers.logging import Priority, log
from src.components.coach_ai.services.openai import retry_embedding_function


def get_semantic_config() -> SemanticConfiguration:
    return SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=None,
            content_fields=[SemanticField(field_name="text")],
        ),
    )


def get_fields() -> List:
    vector_dimensions = 1536
    return [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(
            name="text",
            type=SearchFieldDataType.String,
            analyzer_name="en.microsoft",
        ),
        SearchField(
            name="embeddings",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            hidden=False,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name="hnswConfigProfile",
        ),
        SearchableField(
            name="metadata",
            type=SearchFieldDataType.String,
            searchable=False,
        ),
        # TODO: Make searchable
        SimpleField(
            name="class",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="type",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="split_uuid",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="split_idx",
            type=SearchFieldDataType.Int32,
            sortable=True,
            filterable=True,
        ),
        SimpleField(
            name="doc_uuid",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="doc_idx",
            type=SearchFieldDataType.Int32,
            sortable=True,
            filterable=True,
        ),
        SimpleField(
            name="permitted_roles",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
        ),
        SimpleField(
            name="source_path",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="pages",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Int32),
            filterable=True,
        ),
    ]


def get_vector_search_config() -> VectorSearch:
    return VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="hnswConfigProfile", algorithm_configuration_name="hnswConfig"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnswConfig",
                parameters=HnswParameters(
                    m=4, ef_construction=400, ef_search=500, metric="cosine"
                ),
            )
        ],
    )


def create_vector_store(index_name: str) -> azuresearch.AzureSearch:
    try:
        # langchain quirk. Can be set as an env var but opted to hardcode it instead.
        azuresearch.FIELDS_CONTENT = "text"
        azuresearch.FIELDS_CONTENT_VECTOR = "embeddings"

        acs_endpoint = f"https://{settings.ACS_SERVICE_NAME}.search.windows.net/"
        acs_key = settings.ACS_ADMIN_KEY
        acs_index = f"{settings.PROJECT_NAME}-{index_name}"
        search_config = get_vector_search_config()
        search_fields = get_fields()
        search_semantic_config = get_semantic_config()
        log.info(f"Creating ACS instance: {acs_index}")

        ai_search = azuresearch.AzureSearch(
            azure_search_endpoint=acs_endpoint,
            azure_search_key=acs_key,
            index_name=acs_index,
            embedding_function=retry_embedding_function,
            semantic_configuration_name="default",
            semantic_configurations=search_semantic_config,
            fields=search_fields,
            vector_search=search_config,
        )

        return ai_search
    except Exception as error:
        log.critical(
            message=str(error),
            instance_name="api-create-vectorstore",
            priority=Priority.P1.value,
        )
        raise error
