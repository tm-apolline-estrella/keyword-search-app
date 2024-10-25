# Import standard library modules
import os
from functools import partial

# Import third-party library modules
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# Import local modules
from src.components.coach_ai.helpers.utils import load_prompt_template

load_prompt_template_from_module = partial(
    load_prompt_template, folder_path=os.path.dirname(os.path.realpath(__file__))
)


REPHRASE_QUESTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            load_prompt_template_from_module("rephrase_question")
        ),
        HumanMessagePromptTemplate.from_template("####Question: {question}####"),
    ]
)


messages = [
    SystemMessagePromptTemplate.from_template(
        load_prompt_template_from_module("qa_vector_db_system")
    ),
    HumanMessagePromptTemplate.from_template("####Question: {question}####"),
]
QA_VECTOR_DB_PROMPT = ChatPromptTemplate.from_messages(messages)
