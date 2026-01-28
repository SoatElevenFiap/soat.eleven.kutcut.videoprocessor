from typing import Annotated

from fastapi import Depends

from modules.shared.services.settings import Settings


def settings_provider():
    return Settings()


SettingsProvider = Annotated[Settings, Depends(settings_provider)]
