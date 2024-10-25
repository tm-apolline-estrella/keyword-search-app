# Import third-party library modules
import openai
from langchain_openai import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Import local modules
from src.components.coach_ai.settings import APIM_END_POINT, APIM_SUB_KEY, MODEL_NAME_EMBEDDINGS

MIN_WAIT_SECONDS = 2
MAX_WAIT_SECONDS = 10
MAX_ATTEMPTS = 6  # need to be hardcoded since we use apim

openai.api_key = APIM_SUB_KEY
openai.azure_endpoint = APIM_END_POINT


class ConfiguredAzureChatOpenAI(AzureChatOpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            openai_api_key=APIM_SUB_KEY,
            azure_endpoint=APIM_END_POINT,
        )


class ConfiguredAzureOpenAIEmbeddings(AzureOpenAIEmbeddings):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            openai_api_key=APIM_SUB_KEY,
            azure_endpoint=APIM_END_POINT,
        )


openai_retry_decorator = retry(
    reraise=True,
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=MIN_WAIT_SECONDS, max=MAX_WAIT_SECONDS),
    retry=(
        retry_if_exception_type(openai.OpenAIError)
        | retry_if_exception_type(openai.APIError)
        | retry_if_exception_type(openai.APIStatusError)
        | retry_if_exception_type(openai.APITimeoutError)
        | retry_if_exception_type(openai.APIConnectionError)
        | retry_if_exception_type(openai.APIResponseValidationError)
        | retry_if_exception_type(openai.BadRequestError)
        | retry_if_exception_type(openai.AuthenticationError)
        | retry_if_exception_type(openai.PermissionDeniedError)
        | retry_if_exception_type(openai.NotFoundError)
        | retry_if_exception_type(openai.ConflictError)
        | retry_if_exception_type(openai.UnprocessableEntityError)
        | retry_if_exception_type(openai.RateLimitError)
        | retry_if_exception_type(openai.InternalServerError)
        | retry_if_exception_type(ValueError)  # e.g. content filter
    ),
)


@openai_retry_decorator
def retry_chain_invoke(chain, *args, **kwargs):
    return chain.invoke(*args, **kwargs)


@openai_retry_decorator
async def retry_chain_ainvoke(chain, *args, **kwargs):
    return await chain.ainvoke(*args, **kwargs)


@openai_retry_decorator
def retry_embedding_function(*args, **kwargs):
    embedding = ConfiguredAzureOpenAIEmbeddings(
        model=MODEL_NAME_EMBEDDINGS,
        azure_deployment=MODEL_NAME_EMBEDDINGS,
    )
    return embedding.embed_query(*args, **kwargs)
