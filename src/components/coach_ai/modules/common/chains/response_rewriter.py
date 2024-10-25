# Import third-party library modules
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.common.prompts import REWRITE_RESPONSE_PROMPT
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import MODEL_NAME_CHAT


def rewrite_response_with_instruction(
    callback_handler: AsyncCallbackHandler,
):
    log.info("Creating RewriteResponseLLM", "api-response-writer")
    rewrite_response_llm = ConfiguredAzureChatOpenAI(
        model_name=MODEL_NAME_CHAT,
        azure_deployment=MODEL_NAME_CHAT,
        callbacks=[callback_handler],
        streaming=True,
        temperature=0,
        verbose=True,
    )

    return REWRITE_RESPONSE_PROMPT | rewrite_response_llm | StrOutputParser()
