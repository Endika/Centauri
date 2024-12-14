from abc import ABC, abstractmethod


class MemoryPort(ABC):
    @abstractmethod
    def create_session(self) -> str:
        raise NotImplementedError(
            "The method ´create_session´ must be implemented."
        )

    @abstractmethod
    def session_exists(self, chat_id: str) -> bool:
        raise NotImplementedError(
            "The method ´session_exists´ must be implemented."
        )

    @abstractmethod
    def run_chat(self, chat_id: str, user_message: str, uuid: str) -> str:
        raise NotImplementedError("The method ´run_chat´ must be implemented.")

    @abstractmethod
    def clear_session(self, chat_id: str) -> None:
        raise NotImplementedError(
            "The method ´clear_session´ must be implemented."
        )
