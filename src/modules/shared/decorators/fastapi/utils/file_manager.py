import inspect
import os
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from typing import List


@dataclass
class FileEntity:
    name: str
    path: str


class FileManager:
    @staticmethod
    def find_files_in_project(end_with: str) -> List[FileEntity]:
        files: List[FileEntity] = []
        path = os.getcwd()
        for root, _, finded_files in os.walk(path):
            for file in finded_files:
                if file.endswith(end_with):
                    file_entity = FileEntity(name=file, path=os.path.join(root, file))
                    files.append(file_entity)
        return files

    @staticmethod
    def get_file_class_instance(
        file_entity: FileEntity, match_class: type
    ) -> list[str]:
        instances = []
        module_name = os.path.splitext(file_entity.name)[0]
        spec = spec_from_file_location(module_name, file_entity.path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name == match_class.__name__:
                continue
            if name.endswith("Controller") and issubclass(obj, match_class):
                instances.append(obj())
        return instances
