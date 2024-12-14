import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.websockets import WebSocket
from app.adapters.websocket_api import WebSocketAPI
from app.core.chat_service import ChatService
from app.core.exceptions import (
    ChatNotFoundError,
    EmptyMessageError,
    InvalidReponseError,
    InvalidRequestIdError,
    ResponseTooLongError,
)
from app.adapters.dtos.errors import ErrorResponseDTO


@pytest.fixture
def mock_chat_service():
    return MagicMock(spec=ChatService)


@pytest.fixture
def mock_websocket():
    websocket = AsyncMock(spec=WebSocket)
    websocket.receive_text.return_value = "Test message"
    return websocket


@pytest.fixture
def websocket_api(mock_chat_service):
    return WebSocketAPI(chat_service=mock_chat_service)


@pytest.mark.asyncio
async def test_handle_connection_new_chat(websocket_api, mock_chat_service, mock_websocket):
    mock_chat_service.create_chat.return_value = "mock_chat_id"

    await websocket_api.handle_connection(mock_websocket)

    mock_chat_service.create_chat.assert_called_once()
    mock_websocket.send_text.assert_any_call('chat_id": mock_chat_id')


@pytest.mark.asyncio
async def test_handle_connection_existing_chat(websocket_api, mock_chat_service, mock_websocket):
    mock_chat_service.chat_exists.return_value = True

    await websocket_api.handle_connection(mock_websocket, chat_id="existing_chat_id")

    mock_chat_service.chat_exists.assert_called_once_with("existing_chat_id")
    mock_websocket.send_text.assert_called()


@pytest.mark.asyncio
async def test_handle_connection_chat_not_found(websocket_api, mock_chat_service, mock_websocket):
    mock_chat_service.chat_exists.side_effect = ChatNotFoundError("nonexistent_chat_id")

    await websocket_api.handle_connection(mock_websocket, chat_id="nonexistent_chat_id")

    mock_chat_service.chat_exists.assert_called_once_with("nonexistent_chat_id")
    mock_websocket.send_json.assert_called_once_with(
        ErrorResponseDTO(
            status="error", code=404, error="ChatNotFound", message="Not found."
        ).dict()
    )


@pytest.mark.asyncio
async def test_handle_connection_process_message(websocket_api, mock_chat_service, mock_websocket):
    mock_chat_service.process_message.return_value = "Response message"

    await websocket_api.handle_connection(mock_websocket, chat_id="mock_chat_id")

    mock_chat_service.process_message.assert_called()
    mock_websocket.send_text.assert_any_call("Response message")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception,code,error_type,message",
    [
        (InvalidRequestIdError("invalid_request_id"), 400, "BadRequest", "Bad Request."),
        (ResponseTooLongError("response too long", 200), 400, "BadRequest", "Bad Request."),
        (EmptyMessageError("empty_message"), 400, "BadRequest", "Bad Request."),
        (InvalidReponseError("invalid_response"), 400, "BadRequest", "Bad Request."),
    ],
)
async def test_handle_connection_exceptions(
    websocket_api, mock_chat_service, mock_websocket, exception, code, error_type, message
):
    mock_chat_service.process_message.side_effect = exception

    await websocket_api.handle_connection(mock_websocket, chat_id="mock_chat_id")

    mock_websocket.send_json.assert_called_once_with(
        ErrorResponseDTO(status="error", code=code, error=error_type, message=message).dict()
    )


@pytest.mark.asyncio
async def test_handle_connection_unexpected_exception(websocket_api, mock_chat_service, mock_websocket):
    mock_chat_service.process_message.side_effect = Exception("Unexpected error")

    await websocket_api.handle_connection(mock_websocket, chat_id="mock_chat_id")

    mock_websocket.send_json.assert_called_once_with(
        ErrorResponseDTO(
            status="error", code=500, error="ServerError", message="Internal server error."
        ).dict()
    )
