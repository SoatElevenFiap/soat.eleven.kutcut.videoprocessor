from typing import Annotated

from fastapi import Depends
from modules.video.services.application import GetVideoProcessApplicationService

def get_video_process_application_service_provider():
    return GetVideoProcessApplicationService()

GetVideoProcessApplicationServiceProvider = Annotated[GetVideoProcessApplicationService, Depends(get_video_process_application_service_provider)]