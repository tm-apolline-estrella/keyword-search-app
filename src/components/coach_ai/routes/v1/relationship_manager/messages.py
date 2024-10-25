# Import standard library modules
from datetime import datetime
from typing import List

# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import local modules
from database import get_db
from helpers.logging import log
from models import Conversation, Message, MessageSource, MessageSuggestion
from schema.relationship_manager.messages import (
    PatchUpdateMessage,
    PostMessageSources,
    PostMessageSuggestions,
    PostSaveConversationMessage,
)
from schema.relationship_manager.responses import MessageBaseResponse

router = APIRouter()


@router.post(
    "/api/v1/relationship-manager/messages", response_model=List[MessageBaseResponse]
)
async def post_message(
    body: PostSaveConversationMessage, db: Session = Depends(get_db)
):
    try:
        user_message = Message(
            conversationId=body.conversation_id,
            is_bot=False,
            text=body.user_text,
            token_count=body.user_token_count,
        )
        bot_message = Message(
            conversationId=body.conversation_id,
            is_bot=True,
            text=body.bot_text,
            token_count=body.bot_token_count,
        )
        db.query(Conversation).filter(Conversation.id == body.conversation_id).update(
            {
                "lastMessageDate": datetime.now(),
            }
        )
        db.add(user_message)
        db.add(bot_message)
        db.commit()
        db.refresh(user_message)
        db.refresh(bot_message)
        return [user_message, bot_message]
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-messages-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.patch(
    "/api/v1/relationship-manager/messages/{message_id}",
    response_model=MessageBaseResponse,
)
async def patch_message(
    message_id: str, body: PatchUpdateMessage, db: Session = Depends(get_db)
):
    try:
        update = {}
        if body.rating is not None:
            update["rating"] = body.rating
            update["ratingData"] = body.rating_data
            update["ratingText"] = body.rating_text
        message = db.query(Message).filter(Message.id == message_id)
        message.update(update)
        db.commit()
        message = message.first()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-messages-patch")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/v1/relationship-manager/messages/{message_id}/sources")
async def post_message_sources(
    message_id: str, body: PostMessageSources, db: Session = Depends(get_db)
):
    try:
        for source in body.sources:
            message_source = MessageSource(
                messageId=message_id,
                link=source.link,
                filename=source.filename,
                chunks=source.chunks,
                dateIngested=source.dateIngested,
            )
            db.add(message_source)
        db.commit()
        return "OK"
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-sources-post")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/api/v1/relationship-manager/messages/{message_id}/suggestions")
async def post_message_suggestions(
    message_id: str, body: PostMessageSuggestions, db: Session = Depends(get_db)
):
    try:
        for suggestion in body.suggestions:
            message_suggestion = MessageSuggestion(
                messageId=message_id,
                suggestion=suggestion,
            )
            db.add(message_suggestion)
        db.commit()
        return "OK"
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-suggestions-post")
        raise HTTPException(status_code=500, detail=str(error))
