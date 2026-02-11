class MessageBrokerAdapter:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name

    async def consume(self, message: str | dict):
        raise NotImplementedError("Method consume must be implemented")
