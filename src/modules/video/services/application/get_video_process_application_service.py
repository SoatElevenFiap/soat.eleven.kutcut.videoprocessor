from modules.shared.adapters import ApplicationService

class GetVideoProcessApplicationService(ApplicationService):
    def __init__(self):
        super().__init__(GetVideoProcessApplicationService.__name__)

    async def process(self, video_id: str):
        self.logger.info(f"Getting video process for video id: {video_id}")
        return {"message": video_id}