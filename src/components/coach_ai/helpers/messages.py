# Import standard library modules
from typing import Dict, List

# Import third-party library modules
import tiktoken

# Import local modules
from schemas import (
    ChatLogResponse,
    ChatMessageResponse,
    ChatProcessStepResponse,
    ChatSourceResponse,
    ChatSuggestionsResponse,
    ChatTokenResponse,
)
from src.components.coach_ai.settings import MODEL_NAME_CHAT

from .utils import format_data


def sender_token_response(sender: str, message: str):
    tokenizer = tiktoken.encoding_for_model(MODEL_NAME_CHAT)
    tokens = tokenizer.encode(message, disallowed_special=())
    token_count = ChatTokenResponse(sender=sender, token_count=len(tokens))
    return format_data(token_count.dict())


def user_stream_message_response(message: str):
    user_stream_message = ChatMessageResponse(
        sender="you", message=message, type="stream"
    )
    return format_data(user_stream_message.dict())


def bot_stream_message_response(message: str):
    bot_stream_message = ChatMessageResponse(
        sender="bot", message=message, type="stream"
    )
    return format_data(bot_stream_message.dict())


def bot_error_response(message: str):
    error = ChatMessageResponse(sender="bot", message=f"Error: {message}", type="error")
    return format_data(error.dict())


def bot_sources_response(sources: List[Dict[str, str]]):
    sources = ChatSourceResponse(sender="bot", sources=sources)
    return format_data(sources.dict())


def bot_source_images_response(images: List[str]):
    source_images = ChatMessageResponse(
        sender="bot", message=images, type="source_images"
    )
    return format_data(source_images.dict())


def bot_suggestions_response(suggestions: List[Dict[str, str]]):
    suggestions = ChatSuggestionsResponse(sender="bot", suggestions=suggestions)
    return format_data(suggestions.dict())


def bot_log_response(log: str):
    log = ChatLogResponse(sender="bot", log=log)
    return format_data(log.dict())


def bot_process_step_response(process_step: str):
    process_step_response = ChatProcessStepResponse(
        sender="bot", process_step=process_step
    )
    return format_data(process_step_response.dict())
