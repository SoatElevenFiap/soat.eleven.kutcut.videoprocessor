from http import HTTPMethod
from typing import Any, Optional, Sequence

from fastapi import APIRouter, Depends, FastAPI

from modules.shared.adapters.fast_api_controller import FastAPIController
from .utils.file_manager import FileManager


class FastAPIManager:
    routes = []

    @staticmethod
    def __normalize_api_path(path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        if "_" in path:
            path = path.replace("_", "-")
        return path.lower()

    @staticmethod
    def __get_controllers() -> list[FastAPIController]:
        instances = []
        file_manager = FileManager.find_files_in_project("_controller.py")
        for file in file_manager:
            test = FileManager.get_file_class_instance(file, FastAPIController)
            if not test:
                continue
            instances.append(test[0])
        return instances

    @staticmethod
    def register_route(route: str, method: str, path: str):
        FastAPIManager.routes.append(
            {
                "route": route,
                "method": method,
                "path": path,
            }
        )

    @staticmethod
    def initialize(app: FastAPI, prefix: str = None):
        for controller in FastAPIManager.__get_controllers():
            if not hasattr(controller, "router") or not controller.router:
                raise ValueError(
                    f"Router not found in {controller.__class__.__name__} did you forget to use @FastAPIManager.controller decorator?"
                )
            app.include_router(controller.router, prefix=prefix or "")

    @staticmethod
    def controller(
        prefix: str,
        tags: Optional[list[str] | str] = None,
        version: Optional[str] = "v1",
    ):
        def decorator(cls):
            class Wrapper(cls, FastAPIController):
                def __init__(self, *args, **kwargs):
                    current_tags = [tags] if isinstance(tags, str) else tags
                    full_prefix = f"/{version}/{prefix}" if prefix else f"/{version}"
                    self.router = APIRouter(prefix=full_prefix, tags=current_tags)
                    super().__init__(*args, **kwargs)
                    for attr_name in dir(self):
                        attr = getattr(self, attr_name)
                        if hasattr(attr, "_route"):
                            (
                                path,
                                method,
                                dependencies,
                                summary,
                                description,
                                response_model,
                            ) = attr._route
                            self.router.add_api_route(
                                path,
                                attr,
                                methods=[method],
                                dependencies=dependencies,
                                summary=summary,
                                description=description,
                                response_model=response_model,
                            )

            return Wrapper

        return decorator

    @staticmethod
    def route(
        path: str,
        method: HTTPMethod,
        dependencies: Sequence[Depends] = None,
        summary: str = None,
        description: str = None,
        response_model: Any = None,
    ):
        normalized_path = FastAPIManager.__normalize_api_path(path)

        def decorator(func):
            func._route = (
                normalized_path,
                method.value,
                dependencies,
                summary,
                description,
                response_model,
            )
            return func

        return decorator
