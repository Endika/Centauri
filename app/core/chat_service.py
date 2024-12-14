import json
import logging

from pydantic import ValidationError

from app.config import MAX_RESPONSE_LENGTH
from app.core.constants import PROMPT_TEMPLATE
from app.core.dtos.responses import ChatResponseDTO
from app.core.exceptions import (ChatNotFoundError, InvalidReponseError,
                                 InvalidRequestIdError, ResponseTooLongError)
from app.ports.chat_port import ChatPort
from app.ports.memory_port import MemoryPort

logger = logging.getLogger(__name__)


class ChatService(ChatPort):
    def __init__(self, memory_manager: MemoryPort):
        self.memory_manager = memory_manager
        self.prompt = PROMPT_TEMPLATE

    def chat_exists(self, chat_id: str) -> bool:
        if not self.memory_manager.session_exists(chat_id):
            return False
        return True

    def create_chat(self) -> str:
        return self.memory_manager.create_session()

    def process_message(
        self, chat_id: str, user_message: str, request_id: str
    ) -> str:
        formatted_message = self.prompt.format(
            max_response=MAX_RESPONSE_LENGTH,
            input=user_message,
            request_id=request_id,
        )

        raw_response = self.memory_manager.run_chat(
            chat_id, formatted_message, request_id
        )

        try:
            content_dict = json.loads(raw_response.content)
            validated_response = ChatResponseDTO(**content_dict)
            response = validated_response.response
        except ValidationError as e:
            logger.error(f"Error occurred: {e}")
            raise InvalidReponseError(raw_response)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise e

        if request_id != validated_response.request_id:
            raise InvalidRequestIdError(validated_response.request_id)

        if len(response) > MAX_RESPONSE_LENGTH:
            raise ResponseTooLongError(response, MAX_RESPONSE_LENGTH)

        return response

    def reset_memory(self, chat_id: str) -> None:
        if not self.memory_manager.session_exists(chat_id):
            raise ChatNotFoundError(chat_id)
        self.memory_manager.clear_session(chat_id)
