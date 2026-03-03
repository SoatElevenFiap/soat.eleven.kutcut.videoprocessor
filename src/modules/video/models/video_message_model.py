from pydantic import BaseModel, ConfigDict, Field


class VideoMessageModel(BaseModel):
    user_id: str = Field(alias="userId")
    filename: str
    title: str = ""
    message_id: str = Field(alias="messageId")
    model_config = ConfigDict(populate_by_name=True)
