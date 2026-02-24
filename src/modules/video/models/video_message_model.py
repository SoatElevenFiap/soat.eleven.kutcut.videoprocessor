from pydantic import BaseModel, Field


class VideoMessageModel(BaseModel):
    user_id: str = Field(alias="userId")
    filename: str
    message_id: str = Field(alias="messageId")

    class Config:
        populate_by_name = True
