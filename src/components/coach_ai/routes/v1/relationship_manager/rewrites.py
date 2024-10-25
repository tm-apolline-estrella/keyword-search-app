# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import local modules
from database import get_db
from helpers.logging import log
from models import RewriteResponse
from schema.relationship_manager.responses import RewriteResponseBaseResponse
from schema.relationship_manager.rewrites import PostCreateRewrite

router = APIRouter()


@router.post(
    "/api/v1/relationship-manager/rewrites/{message_id}",
    response_model=RewriteResponseBaseResponse,
)
async def post_rewrites(
    message_id: str, body: PostCreateRewrite, db: Session = Depends(get_db)
):
    try:
        rewrite = RewriteResponse(
            messageId=message_id,
            instruction=body.instruction,
            rewriteText=body.rewrite_text,
        )
        db.add(rewrite)
        db.commit()
        db.refresh(rewrite)
        return rewrite
    except Exception as error:
        log.error(message=str(error), instance_name="api-rm-rewrites-post")
        raise HTTPException(status_code=500, detail=str(error))
