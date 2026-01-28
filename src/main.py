import os

import pytomlpp
from fastapi import FastAPI

from modules.shared.decorators import FastAPIManager
from modules.shared.middlewares import HttpCorrelationMiddleware
from modules.shared.providers import SettingsProvider

app = FastAPI()
FastAPIManager.initialize(app)

app.add_middleware(HttpCorrelationMiddleware)

@app.get("/health-check", tags=["Health"])
async def health_check(settings: SettingsProvider):
    project_info = pytomlpp.load(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
    )
    return {
        "message": "Video Processor is running",
        "version": project_info["project"]["version"],
        "environment": settings.environment,
    }
