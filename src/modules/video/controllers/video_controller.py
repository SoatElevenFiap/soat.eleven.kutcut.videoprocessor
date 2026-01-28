from modules.shared.adapters import FastAPIController
from modules.shared.decorators import FastAPIManager
from http import HTTPMethod

from modules.video.providers.get_video_process_application_service_provider import GetVideoProcessApplicationServiceProvider

@FastAPIManager.controller("video", "Video", version="v1")
class VideoController(FastAPIController):
    def __init__(self):
        super().__init__()

    @FastAPIManager.route("/get-process", method=HTTPMethod.GET)
    async def get_process(self, video_id: str, get_video_process_application_service: GetVideoProcessApplicationServiceProvider):
        return await get_video_process_application_service.process(video_id)