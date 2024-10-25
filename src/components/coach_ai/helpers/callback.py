# Import standard library modules
import asyncio
from typing import Any, Dict, List

# Import third-party library modules
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult

# Import local modules
from src.components.coach_ai.helpers.logging import log


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.queue.put(token)  # Stream tokens

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        log.info("StreamHandler: LLM START", "api-callback")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        log.info("StreamHandler: LLM END", "api-callback")
        await self.queue.put("[DONE]")  # Signal to stop streaming


class NonStreamingLLMCallbackHandler(AsyncCallbackHandler):
    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        log.info("NonStreamHandler: LLM START", "api-callback")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        log.info("NonStreamHandler: LLM END", "api-callback")
