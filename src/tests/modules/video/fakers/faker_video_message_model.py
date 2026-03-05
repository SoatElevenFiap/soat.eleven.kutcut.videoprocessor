from typing import Optional

from faker import Faker

from modules.video.models.video_message_model import VideoMessageModel


class FakerVideoMessageModel:
    @staticmethod
    def create(payload: Optional[dict[str, any]] = None) -> VideoMessageModel:
        if not payload:
            payload = {}

        faker = Faker()
        default_payload = {
            "user_id": faker.uuid4(),
            "filename": faker.file_name(category="video"),
            "title": faker.sentence(),
            "message_id": faker.uuid4(),
        }
        return VideoMessageModel(**{**default_payload, **payload})
