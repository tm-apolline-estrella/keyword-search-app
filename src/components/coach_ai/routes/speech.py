# Import third-party library modules
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.services.az_speech import azure_text_to_speech

router = APIRouter()


@router.post("/api/speech")
async def text_to_speech(
    req: Request,
):
    try:
        email = req.state.user_email
        with log.contextualize(
            user=email, ip=req.client.host, method=req.method, path=req.url.path
        ):
            body = await req.json()
            phrase = body["phrase"]
            audio_stream = azure_text_to_speech(phrase)
            return StreamingResponse(
                audio_stream,
                media_type="audio/mpeg",
                headers={
                    "Content-Type": "audio/mpeg",
                    "Transfer-Encoding": "chunked",
                },
            )
    except Exception as error:
        log.error(message=str(error), instance_name="api-coach-speech")
        raise HTTPException(status_code=500, detail=str(error))
