class ChatNotFoundError(Exception):
    def __init__(self, chat_id: str):
        super().__init__(f"Chat with ID '{chat_id}' not found.")
        self.chat_id = chat_id


class InvalidRequestIdError(Exception):
    def __init__(self, uuid: str):
        super().__init__(f"The UUID '{uuid}' not is valid.")
        self.uuid = uuid


class ResponseTooLongError(Exception):
    def __init__(self, response: str, max_length: int):
        super().__init__(
            f"The response exceeds the {max_length} character limit."
        )
        self.response = response
        self.max_length = max_length


class EmptyMessageError(Exception):
    def __init__(self, response: str):
        super().__init__("Empty message.")
        self.response = response


class InvalidReponseError(Exception):
    def __init__(self, response: str):
        super().__init__("The AI response is not valid.")
        self.uuid = response
