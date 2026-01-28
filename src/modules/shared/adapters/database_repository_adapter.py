from modules.shared.adapters.repository_adapter import RepositoryAdapter


class DatabaseRepositoryAdapter(RepositoryAdapter):
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name