from abc import ABC

from fastapi import APIRouter


class FastAPIController(ABC):
    router: APIRouter
