# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import desc, null
from sqlalchemy.orm import Session, selectinload

# Import local modules
from database import get_db
from helpers.logging import log
from models import KnowledgebaseConversation, KnowledgebaseMessage
from schema.librarian.conversations import (
    ConversationPatchRequest,
    ConversationPostRequest,
)
from schema.librarian.responses import KnowledgebaseConversationBaseResponse

router = APIRouter()


@router.get(
    "/api/v1/librarian/conversations/{conversation_id}",
    response_model=KnowledgebaseConversationBaseResponse | None,
)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        conversation = (
            db.query(KnowledgebaseConversation)
            .options(
                selectinload(KnowledgebaseConversation.messages).options(
                    selectinload(KnowledgebaseMessage.messageSources),
                    selectinload(KnowledgebaseMessage.messageSuggestions),
                    selectinload(KnowledgebaseMessage.messageRewriteResponses),
                )
            )
            .filter(
                KnowledgebaseConversation.id == conversation_id,
                KnowledgebaseConversation.deletedAt == null(),
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
        log.error(message=str(error), instance_name="api-librarian-conversation-get")
        raise HTTPException(status_code=500, detail=str(error))


@router.get(
    "/api/v1/librarian/conversations",
    response_model=List[KnowledgebaseConversationBaseResponse],
)
async def get_conversations(user_id: str, db: Session = Depends(get_db)):
    try:
        conversations = (
            db.query(KnowledgebaseConversation)
            .filter(
                KnowledgebaseConversation.userId == user_id,
                KnowledgebaseConversation.deletedAt == null(),
            )
            .order_by(desc(KnowledgebaseConversation.lastMessageDate))
            .all()
        )
        return conversations
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-conversations-get")
        raise HTTPException(status_code=500, detail=str(error))


@router.post(
    "/api/v1/librarian/conversations/{conversation_id}",
    response_model=KnowledgebaseConversationBaseResponse,
)
async def post_conversation(
    conversation_id: str, body: ConversationPostRequest, db: Session = Depends(get_db)
):
    try:
        conversation = KnowledgebaseConversation(
            id=conversation_id, userId=body.user_id, title=body.title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-conversations-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.patch(
    "/api/v1/librarian/conversations/{conversation_id}",
    response_model=KnowledgebaseConversationBaseResponse,
)
async def patch_conversation(
    conversation_id: str, body: ConversationPatchRequest, db: Session = Depends(get_db)
):
    try:
        conversation = (
            db.query(KnowledgebaseConversation)
            .filter(KnowledgebaseConversation.id == conversation_id)
            .first()
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} does not exist",
            )
        columns_to_update = body.model_dump()
        for key, value in columns_to_update.items():
            if value is not None:
                setattr(conversation, key, value)
        db.commit()
        conversation = (
            db.query(KnowledgebaseConversation)
            .filter(KnowledgebaseConversation.id == conversation_id)
            .first()
        )
        return conversation
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-conversations-patch")
        raise HTTPException(status_code=500, detail=str(error))


@router.delete(
    "/api/v1/librarian/conversations/{conversation_id}",
    response_model=KnowledgebaseConversationBaseResponse,
)
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        deleted_conversation = (
            db.query(KnowledgebaseConversation)
            .filter(KnowledgebaseConversation.id == conversation_id)
            .first()
        )
        if deleted_conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} does not exist",
            )
        deleted_conversation.deletedAt = datetime.now()
        db.commit()
        return deleted_conversation
    except Exception as error:
        log.error(
            message=str(error), instance_name="api-librarian-conversations-delete"
        )
        raise HTTPException(status_code=500, detail=str(error))
