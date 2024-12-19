from uuid import uuid4

from app.adapters.vector_db_adapter import VectorDBAdapter
from app.ports.chat_port import ChatPort


class HelpCenterService(ChatPort):
    def __init__(self, vector_db_adapter: VectorDBAdapter):
        self.vector_db = vector_db_adapter

    def create_chat(self) -> str:
        # sorry i know i can reuse it but I wanted to give you the value.
        return str(uuid4())

    def load_help_center(self, file_path: str):
        self.vector_db.load_and_store_documents(file_path)

    def _get_answer(self, question: str):
        return self.vector_db.query(question)

    def process_message(
        self, chat_id: str, user_message: str, request_id: str
    ) -> str:
        return self._get_answer(user_message)

    def reset_memory(self, chat_id: str) -> None:
        pass
