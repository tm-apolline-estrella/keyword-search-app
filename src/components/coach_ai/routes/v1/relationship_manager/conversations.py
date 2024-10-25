# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, null
from sqlalchemy.orm import Session, selectinload

# Import local modules
from database import get_db
from helpers.logging import log
from models import Conversation, Message
from schema.relationship_manager.conversations import (
    PatchUpdateConversation,
    PostCreateConversation,
)
from schema.relationship_manager.responses import ConversationBaseResponse

router = APIRouter()


@router.get(
    "/api/v1/relationship-manager/conversations/{conversation_id}",
    response_model=ConversationBaseResponse | None,
)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        conversation = (
            db.query(Conversation)
            .options(
                selectinload(Conversation.messages).selectinload(Message.messageSources)
            )
            .options(
                selectinload(Conversation.messages).selectinload(
                    Message.messageSuggestions
                )
            )
            .options(
                selectinload(Conversation.messages).selectinload(
                    Message.messageRewriteResponses
                )
            )
            .filter(
                Conversation.id == conversation_id, Conversation.deletedAt == null()
            )
            .first()
        )
        if conversation:
            conversation.messages = sorted(
                conversation.messages,
                key=lambda message: (message.createdAt, message.is_bot),
            )
        return conversation
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-conversation-get")
        raise HTTPException(status_code=500, detail=str(error))


@router.get(
    "/api/v1/relationship-manager/conversations",
    response_model=List[ConversationBaseResponse],
)
async def get_conversations(user_id: str, db: Session = Depends(get_db)):
    try:
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.userId == user_id,
                Conversation.deletedAt == null(),
            )
            .order_by(desc(Conversation.lastMessageDate))
            .all()
        )
        return conversations
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-conversations-get")
        raise HTTPException(status_code=500, detail=str(error))


@router.post(
    "/api/v1/relationship-manager/conversations/{conversation_id}",
    response_model=ConversationBaseResponse,
)
async def post_conversation(
    conversation_id: str, body: PostCreateConversation, db: Session = Depends(get_db)
):
    try:
        conversation = Conversation(
            id=conversation_id, userId=body.user_id, title=body.title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-conversations-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.delete("/api/v1/relationship-manager/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        db.query(Conversation).filter(Conversation.id == conversation_id).update(
            {"deletedAt": datetime.now()}
        )
        db.commit()
        return None
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-conversations-delete")
        raise HTTPException(status_code=500, detail=str(error))


@router.patch(
    "/api/v1/relationship-manager/conversations/{conversation_id}",
    response_model=ConversationBaseResponse,
)
async def patch_conversation(
    conversation_id: str, body: PatchUpdateConversation, db: Session = Depends(get_db)
):
    try:
        update_data = {}

        if body.pinned_at is not None:
            update_data["pinnedAt"] = datetime.now() if body.pinned_at else None

        if body.last_message_date is not None:
            update_data["lastMessageDate"] = body.last_message_date

        conversation = db.query(Conversation).filter(Conversation.id == conversation_id)

        conversation.update(update_data)
        db.commit()
        conversation = conversation.first()
        return conversation
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-conversations-patch")
        raise HTTPException(status_code=500, detail=str(error))
