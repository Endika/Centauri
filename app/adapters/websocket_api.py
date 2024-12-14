import logging
from uuid import uuid4

from fastapi import WebSocket

from app.adapters.dtos.errors import ErrorResponseDTO
from app.core.chat_service import ChatService
from app.core.exceptions import (ChatNotFoundError, EmptyMessageError,
                                 InvalidReponseError, InvalidRequestIdError,
                                 ResponseTooLongError)

logger = logging.getLogger(__name__)


class WebSocketAPI:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def handle_connection(
        self, websocket: WebSocket, chat_id: str = None
    ):
        await websocket.accept()

        if not chat_id:
            chat_id = self.chat_service.create_chat()
            await websocket.send_text(f'chat_id": {str(chat_id)}')
        elif self.chat_service.chat_exists(chat_id):
            raise ChatNotFoundError(chat_id)

        while True:
            try:

                data = await websocket.receive_text()
                response = self.chat_service.process_message(
                    chat_id, data, str(uuid4())
                )
                await websocket.send_text(response)

            except ChatNotFoundError as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 404, "ChatNotFound", "Not found."
                )
            except InvalidRequestIdError as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 400, "BadRequest", "Bad Request."
                )
            except ResponseTooLongError as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 400, "BadRequest", "Bad Request."
                )
            except EmptyMessageError as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 400, "BadRequest", "Bad Request."
                )
            except InvalidReponseError as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 400, "BadRequest", "Bad Request."
                )
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                await self.send_error(
                    websocket, 500, "ServerError", "Internal server error."
                )

    async def send_error(
        self, websocket: WebSocket, code: int, error_type: str, message: str
    ):
        error_response = ErrorResponseDTO(
            status="error", code=code, error=error_type, message=message
        )
        await websocket.send_json(error_response.dict())
