from __future__ import annotations

# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from pydantic import BaseModel


class UserBaseResponse(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    email_verified: datetime | None = None
    image: str | None = None
    createdAt: datetime
    updatedAt: datetime


class UserConversationsResponse(UserBaseResponse):
    conversations: List[ConversationBaseResponse]
    knowledgebaseConversations: List[KnowledgebaseConversationBaseResponse]


# Import local modules
# Import schema dependencies last to avoid circular dependencies errors
from schema.librarian.responses import (  # noqa: E402
    KnowledgebaseConversationBaseResponse,
)
from schema.relationship_manager.responses import ConversationBaseResponse  # noqa: E402

# Rebuild models that have circular dependencies
UserBaseResponse.model_rebuild()
