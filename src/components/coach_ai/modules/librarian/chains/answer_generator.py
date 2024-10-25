# Import third-party library modules
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.librarian.prompts import QA_VECTOR_DB_PROMPT
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import MODEL_NAME_CHAT


def answer_question_based_on_context(
    stream_handler: AsyncCallbackHandler,
):

    log.info("Creating StreamingLLM", "api-answer-generator")
    streaming_llm = ConfiguredAzureChatOpenAI(
        model_name=MODEL_NAME_CHAT,
        azure_deployment=MODEL_NAME_CHAT,
        callbacks=[stream_handler],
        streaming=True,
        temperature=0,
        verbose=True,
    )

    return QA_VECTOR_DB_PROMPT | streaming_llm | StrOutputParser()
