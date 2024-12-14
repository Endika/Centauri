from abc import ABC, abstractmethod


class ChatPort(ABC):
    @abstractmethod
    def process_message(
        self, chat_id: str, user_message: str, uuid: str
    ) -> str:
        raise NotImplementedError(
            "The method ´process_message´ must be implemented."
        )

    @abstractmethod
    def reset_memory(self, chat_id: str) -> None:
        raise NotImplementedError(
            "The method ´reset_memory´ must be implemented."
        )
