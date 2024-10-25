# Import standard library modules
import ast

# Import third-party library modules
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.common.prompts import SUGGEST_QUESTIONS_PROMPT
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import MODEL_NAME_CHAT


def suggest_follow_up_questions(
    callback_handler: AsyncCallbackHandler,
):
    log.info("Creating SuggestQuestionsLLM", "api-chains")
    suggest_questions_llm = ConfiguredAzureChatOpenAI(
        model_name=MODEL_NAME_CHAT,
        azure_deployment=MODEL_NAME_CHAT,
        callbacks=[callback_handler],
        streaming=True,
        temperature=0,
        verbose=True,
    )

    return (
        SUGGEST_QUESTIONS_PROMPT
        | suggest_questions_llm
        | StrOutputParser()
        | ast.literal_eval
    )
