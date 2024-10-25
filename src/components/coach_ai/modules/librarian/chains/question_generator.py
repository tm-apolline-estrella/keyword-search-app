# Import third-party library modules
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.librarian.prompts import REPHRASE_QUESTION_PROMPT
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import MODEL_NAME_CHAT


def rephrase_question_based_on_chat(
    callback_handler: AsyncCallbackHandler,
):

    log.info("Creating RephraseQuestionLLM", "api-question-generator")
    rephrase_question_llm = ConfiguredAzureChatOpenAI(
        model_name=MODEL_NAME_CHAT,
        azure_deployment=MODEL_NAME_CHAT,
        callbacks=[callback_handler],
        temperature=0,
        verbose=True,
    )

    return REPHRASE_QUESTION_PROMPT | rephrase_question_llm | StrOutputParser()
