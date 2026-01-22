from typing import Literal, Optional

from pydantic import BaseModel


class ContentGenerateRequest(BaseModel):
    mode: Literal["image", "video"]
    prompt: str


class ContentGenerateResponse(BaseModel):
    mode: Literal["image", "video"]
    provider: str
    title: str
    caption: str
    hashtags: str
    generation_prompt: str
    notes: Optional[str] = None


