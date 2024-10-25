# Import standard library modules
from datetime import datetime
from typing import Optional

# Import third-party library modules
from pydantic import BaseModel


class ConversationRequest(BaseModel):
    id: str
    user_id: str


class ConversationPatchRequest(BaseModel):
    pinnedAt: Optional[datetime] = None
    lastMessageDate: Optional[datetime] = None


class ConversationPostRequest(BaseModel):
    user_id: str
    title: str
