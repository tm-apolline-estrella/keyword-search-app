# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from pydantic import BaseModel


class MessagePatchRequest(BaseModel):
    rating: bool | None
    rating_data: str | None
    rating_text: str | None


class MessagePostRequest(BaseModel):
    conversation_id: str
    user_text: str
    user_token_count: int
    bot_text: str
    bot_token_count: int


class MessageSourcePostItem(BaseModel):
    link: str
    filename: str
    chunks: str
    dateIngested: datetime | str


class MessageSourcesPostRequest(BaseModel):
    sources: List[MessageSourcePostItem]


class MessageSuggestionsPostRequest(BaseModel):
    suggestions: List[str]
