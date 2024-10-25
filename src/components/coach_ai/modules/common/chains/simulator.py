# Import third-party library modules
from langchain_core.output_parsers import StrOutputParser

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.modules.common.prompts import SIMULATOR_PROMPT
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import MODEL_NAME_CHAT


def get_simulator_chain():
    log.info("Initializing Simulator Chain", "api-simulator")

    simulator_llm = ConfiguredAzureChatOpenAI(
        model_name=MODEL_NAME_CHAT,
        azure_deployment=MODEL_NAME_CHAT,
        temperature=0,
        streaming=False,
    )

    return SIMULATOR_PROMPT | simulator_llm | StrOutputParser()
