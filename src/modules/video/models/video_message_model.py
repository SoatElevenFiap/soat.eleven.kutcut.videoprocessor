from pydantic import BaseModel


class VideoMessageModel(BaseModel):
    user_id: str
    video_id: str
