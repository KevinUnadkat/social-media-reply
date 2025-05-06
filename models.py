from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PostData(BaseModel):
    platform: str = Field(..., description="The social media platform (e.g., Twitter, LinkedIn, Instagram)", examples=["Twitter"])
    post_text: str = Field(..., description="The text content of the original post", examples=["Just launched my new project! #buildinpublic"])

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "LinkedIn",
                "post_text": "Excited to share insights from the recent tech conference. Key takeaways on AI ethics and future trends."
            }
        }

class ReplyResponse(BaseModel):
    platform: str
    post_text: str
    generated_reply: str

class StoredReply(ReplyResponse):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    id: Optional[str] = Field(None, alias="_id") 

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(), 
        }

class ErrorResponse(BaseModel):
    detail: str
