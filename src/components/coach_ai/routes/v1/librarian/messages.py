# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Import local modules
from database import get_db
from helpers.logging import log
from models import (
    KnowledgebaseConversation,
    KnowledgebaseMessage,
    KnowledgebaseMessageSource,
    KnowledgebaseMessageSuggestion,
)
from schema.librarian.messages import (
    MessagePatchRequest,
    MessagePostRequest,
    MessageSourcesPostRequest,
    MessageSuggestionsPostRequest,
)
from schema.librarian.responses import KnowledgebaseMessageBaseResponse

router = APIRouter()


@router.post(
    "/api/v1/librarian/messages", response_model=List[KnowledgebaseMessageBaseResponse]
)
async def post_messages(body: MessagePostRequest, db: Session = Depends(get_db)):
    try:
        user_message = KnowledgebaseMessage(
            conversationId=body.conversation_id,
            is_bot=False,
            text=body.user_text,
            token_count=body.user_token_count,
        )
        bot_message = KnowledgebaseMessage(
            conversationId=body.conversation_id,
            is_bot=True,
            text=body.bot_text,
            token_count=body.bot_token_count,
        )
        conversation = (
            db.query(KnowledgebaseConversation)
            .filter(KnowledgebaseConversation.id == body.conversation_id)
            .first()
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {body.conversation_id} does not exist",
            )
        conversation.lastMessageDate = datetime.now()
        db.add(user_message)
        db.add(bot_message)
        db.commit()
        db.refresh(user_message)
        db.refresh(bot_message)
        return [user_message, bot_message]
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-messages-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.patch(
    "/api/v1/librarian/messages/{message_id}",
    response_model=KnowledgebaseMessageBaseResponse,
)
async def patch_message(
    message_id: str, body: MessagePatchRequest, db: Session = Depends(get_db)
):
    try:
        message = (
            db.query(KnowledgebaseMessage)
            .filter(KnowledgebaseMessage.id == message_id)
            .first()
        )
        if message is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with id {message_id} does not exist",
            )
        message.rating = body.rating
        message.ratingData = body.rating_data
        message.ratingText = body.rating_text
        db.commit()
        db.refresh(message)
        return message
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-messages-patch")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/v1/librarian/messages/{message_id}/sources")
async def post_message_sources(
    message_id: str, body: MessageSourcesPostRequest, db: Session = Depends(get_db)
):
    try:
        for source in body.sources:
            message_source = KnowledgebaseMessageSource(
                messageId=message_id,
                link=source.link,
                filename=source.filename,
                chunks=source.chunks,
                dateIngested=source.dateIngested,
            )
            db.add(message_source)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successfully saved message sources"},
        )
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-sources-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/v1/librarian/messages/{message_id}/suggestions")
async def post_message_suggestions(
    message_id: str, body: MessageSuggestionsPostRequest, db: Session = Depends(get_db)
):
    try:
        for suggestion in body.suggestions:
            message_suggestion = KnowledgebaseMessageSuggestion(
                messageId=message_id,
                suggestion=suggestion,
            )
            db.add(message_suggestion)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successfully csaved message suggestions"},
        )
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-suggestions-post")
        raise HTTPException(status_code=500, detail=str(error))
