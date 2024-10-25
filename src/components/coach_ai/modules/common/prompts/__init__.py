# Import standard library modules
import os
from functools import partial

# Import third-party library modules
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate

# Import local modules
from src.components.coach_ai.helpers.utils import load_prompt_template

load_prompt_template_from_module = partial(
    load_prompt_template, folder_path=os.path.dirname(os.path.realpath(__file__))
)


SUGGEST_QUESTIONS_PROMPT = PromptTemplate.from_template(
    load_prompt_template_from_module("suggest_questions_based_on_answer")
)

REWRITE_RESPONSE_PROMPT = PromptTemplate.from_template(
    load_prompt_template_from_module("rewrite_response")
)

SIMULATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            load_prompt_template_from_module("simulator")
        ),
    ]
)
