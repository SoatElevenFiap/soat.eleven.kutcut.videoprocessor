import sys

from loguru import logger

from modules.shared.middlewares import get_http_correlation_id


class LoggerService:
    def __init__(self, context: str):
        logger.remove()
        logger.level("INFO", color="<white><bg #0066cc>")
        logger.level("WARNING", color="<white><bg #ffcc00>")
        logger.level("ERROR", color="<white><bg #cc0000>")
        logger.level("DEBUG", color="<white><bg #888888>")

        logger.add(
            sys.stdout,
            colorize=True,
            format="     <level> {level:>4} </level>  <yellow>[{extra[correlation_id]}]</yellow> - {message} <dim>({file}:{line})</dim>",
        )
        self.logger = logger.bind(context=context)
        self.logger = self.logger.opt(depth=1, colors=False)

    def debug(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).debug(message)

    def info(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).info(message)

    def warning(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).warning(message)

    def error(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).error(message)

    def title_box(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).info(
            f"╔{'═' * (len(message) + 2)}╗"
        )
        self.logger.bind(correlation_id=get_http_correlation_id()).info(f"║ {message} ║")
        self.logger.bind(correlation_id=get_http_correlation_id()).info(
            f"╚{'═' * (len(message) + 2)}╝"
        )

    def title_box_warning(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).warning(
            f"╔{'═' * (len(message) + 2)}╗"
        )
        self.logger.bind(correlation_id=get_http_correlation_id()).warning(f"║ {message} ║")
        self.logger.bind(correlation_id=get_http_correlation_id()).warning(
            f"╚{'═' * (len(message) + 2)}╝"
        )

    def title_box_error(self, message):
        self.logger.bind(correlation_id=get_http_correlation_id()).error(
            f"╔{'═' * (len(message) + 2)}╗"
        )
        self.logger.bind(correlation_id=get_http_correlation_id()).error(f"║ {message} ║")
        self.logger.bind(correlation_id=get_http_correlation_id()).error(
            f"╚{'═' * (len(message) + 2)}╝"
        )

    def dict_to_table(self, message: dict):
        self.logger.bind(correlation_id=get_http_correlation_id()).info(
            f"╔{'═' * (len(message) + 30)}╗"
        )
        for key, value in message.items():
            self.logger.bind(correlation_id=get_http_correlation_id()).info(
                f"║ {key}: {value}"
            )
        self.logger.bind(correlation_id=get_http_correlation_id()).info(
            f"╚{'═' * (len(message) + 30)}╝"
        )
