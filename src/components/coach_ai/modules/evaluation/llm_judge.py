"""
    This module contains the DeepEvalBaseLLM used for the LLM-as-a-judge metrics.
"""

# Import third-party library modules
from deepeval.models.base_model import DeepEvalBaseLLM

# Import local modules
from src.components.coach_ai.services.openai import ConfiguredAzureChatOpenAI
from src.components.coach_ai.settings import OPENAI_API_DEPLOYMENT_NAME, OPENAI_API_VERSION

################################
#    Evaluator Model Setup     #
################################


class AzureOpenAI(DeepEvalBaseLLM):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return res.content

    def get_model_name(self):
        return "Custom Azure OpenAI Model"


custom_model = ConfiguredAzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION, azure_deployment=OPENAI_API_DEPLOYMENT_NAME
)
azure_openai = AzureOpenAI(model=custom_model)
