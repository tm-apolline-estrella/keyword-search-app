from __future__ import annotations

# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from pydantic import BaseModel


class KnowledgebaseMessageSourceBaseResponse(BaseModel):
    id: str | int
    messageId: str
    link: str
    filename: str
    chunks: str
    dateIngested: datetime
    dateCreated: datetime
    dateDeleted: datetime | None = None


class KnowledgebaseMessageSuggestionBaseResponse(BaseModel):
    id: str
    suggestion: str
    createdAt: datetime
    messageId: str


class KnowledgebaseRewriteResponseBaseResponse(BaseModel):
    id: str
    messageId: str
    instruction: str
    rewriteText: str
    createdAt: datetime


class KnowledgebaseMessageBaseResponse(BaseModel):
    id: str
    conversationId: str
    is_bot: bool
    text: str
    token_count: int
    rating: bool | None = None
    ratingData: str | None = None
    ratingText: str | None = None
    messageSources: List[KnowledgebaseMessageSourceBaseResponse]
    messageSuggestions: List[KnowledgebaseMessageSuggestionBaseResponse]
    messageRewriteResponses: List[KnowledgebaseRewriteResponseBaseResponse]
    createdAt: datetime
    deletedAt: datetime | None = None


class KnowledgebaseConversationBaseResponse(BaseModel):
    id: str
    title: str
    userId: str
    messages: List[KnowledgebaseMessageBaseResponse]
    lastMessageDate: datetime
    createdAt: datetime
    updatedAt: datetime
    deletedAt: datetime | None = None
    pinnedAt: datetime | None = None


class KnowledgebaseConversationUserResponse(KnowledgebaseConversationBaseResponse):
    user: UserBaseResponse


# Import local modules
# Import schema dependencies last to avoid circular dependencies errors
from schema.user.responses import UserBaseResponse  # noqa: E402

# Rebuild models that have circular dependencies
KnowledgebaseConversationUserResponse.model_rebuild()
