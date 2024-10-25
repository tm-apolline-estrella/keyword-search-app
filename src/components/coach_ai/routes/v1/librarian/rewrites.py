# Import third-party library modules
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import local modules
from database import get_db
from helpers.logging import log
from models import KnowledgebaseRewriteResponse
from schema.librarian.responses import KnowledgebaseRewriteResponseBaseResponse
from schema.librarian.rewrites import RewritesPostRequest

router = APIRouter()


@router.post(
    "/api/v1/librarian/rewrites/{message_id}",
    response_model=KnowledgebaseRewriteResponseBaseResponse,
)
async def post_rewrite(
    message_id: str, body: RewritesPostRequest, db: Session = Depends(get_db)
):
    try:
        rewrite = KnowledgebaseRewriteResponse(
            messageId=message_id,
            instruction=body.instruction,
            rewriteText=body.rewrite_text,
        )
        db.add(rewrite)
        db.commit()
        db.refresh(rewrite)
        return rewrite
    except Exception as error:
        log.error(message=str(error), instance_name="api-librarian-rewrites-post")
        raise HTTPException(status_code=500, detail=str(error))
