# Import third-party library modules
from pydantic import BaseModel


class RewritesPostRequest(BaseModel):
    instruction: str
    rewrite_text: str
