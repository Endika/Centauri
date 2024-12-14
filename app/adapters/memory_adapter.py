import uuid
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.config import OPEN_API_KEY
from app.core.exceptions import ChatNotFoundError
from app.ports.memory_port import MemoryPort


class MemoryManager(MemoryPort):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            # if the application grows too large we can use Redis and DDBB
            # to store the IDs if is necessary
            cls._instance.sessions = {}
            cls._instance.store = {}
        return cls._instance

    def create_session(self) -> str:
        chat_id = str(uuid.uuid4())
        chat_model = ChatOpenAI(temperature=0.7, openai_api_key=OPEN_API_KEY)

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in self.store:
                self.store[session_id] = InMemoryHistory()
            return self.store[session_id]

        self.sessions[chat_id] = RunnableWithMessageHistory(
            runnable=chat_model, get_session_history=get_session_history
        )
        return chat_id

    def session_exists(self, chat_id: str) -> bool:
        return chat_id in self.sessions

    def run_chat(self, chat_id: str, user_message: str, uuid: str) -> str:
        if chat_id not in self.sessions:
            raise ChatNotFoundError(chat_id)
        runnable_with_history = self.sessions[chat_id]
        config = {"configurable": {"session_id": chat_id}}
        return runnable_with_history.invoke({"input": user_message}, config)

    def clear_session(self, chat_id: str) -> None:
        if chat_id in self.sessions:
            self.sessions[chat_id].memory.clear()


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []
