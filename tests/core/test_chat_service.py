import pytest
from unittest.mock import MagicMock
from app.core.chat_service import ChatService
from app.core.dtos.responses import ChatResponseDTO
from pydantic import ValidationError
from app.core.exceptions import (
    ChatNotFoundError,
    InvalidReponseError,
    InvalidRequestIdError,
    ResponseTooLongError,
)
from app.ports.memory_port import MemoryPort


@pytest.fixture
def mock_memory_manager():
    return MagicMock(spec=MemoryPort)


@pytest.fixture
def chat_service(mock_memory_manager):
    return ChatService(memory_manager=mock_memory_manager)


def test_create_chat(chat_service, mock_memory_manager):
    mock_memory_manager.create_session.return_value = "mock_chat_id"

    chat_id = chat_service.create_chat()

    assert chat_id == "mock_chat_id"
    mock_memory_manager.create_session.assert_called_once()


def test_chat_exists(chat_service, mock_memory_manager):
    mock_memory_manager.session_exists.return_value = True

    assert chat_service.chat_exists("mock_chat_id") is True
    mock_memory_manager.session_exists.assert_called_once_with("mock_chat_id")

    mock_memory_manager.session_exists.return_value = False
    assert chat_service.chat_exists("nonexistent_chat_id") is False


def test_process_message_valid_response(chat_service, mock_memory_manager):
    raw_response = {"request_id": "mock_request_id", "response": "Valid response"}
    mock_memory_manager.run_chat.return_value = raw_response

    response = chat_service.process_message(
        chat_id="mock_chat_id",
        user_message="Hello!",
        request_id="mock_request_id",
    )

    assert response == raw_response["response"]
    mock_memory_manager.run_chat.assert_called_once()


def test_process_message_invalid_request_id(chat_service, mock_memory_manager):
    raw_response = {"request_id": "different_request_id", "response": "Response"}
    mock_memory_manager.run_chat.return_value = raw_response

    with pytest.raises(InvalidRequestIdError):
        chat_service.process_message(
            chat_id="mock_chat_id",
            user_message="Hello!",
            request_id="mock_request_id",
        )


def test_process_message_response_too_long(chat_service, mock_memory_manager):
    long_response = "x" * 300  # Simula una respuesta más larga que MAX_RESPONSE_LENGTH
    raw_response = {"request_id": "mock_request_id", "response": long_response}
    mock_memory_manager.run_chat.return_value = raw_response

    with pytest.raises(ResponseTooLongError):
        chat_service.process_message(
            chat_id="mock_chat_id",
            user_message="Hello!",
            request_id="mock_request_id",
        )


def test_process_message_invalid_response(chat_service, mock_memory_manager):
    invalid_response = {"invalid_field": "value"}
    mock_memory_manager.run_chat.return_value = invalid_response

    with pytest.raises(InvalidReponseError):
        chat_service.process_message(
            chat_id="mock_chat_id",
            user_message="Hello!",
            request_id="mock_request_id",
        )


def test_reset_memory(chat_service, mock_memory_manager):
    mock_memory_manager.session_exists.return_value = True

    chat_service.reset_memory("mock_chat_id")
    mock_memory_manager.clear_session.assert_called_once_with("mock_chat_id")


def test_reset_memory_not_found(chat_service, mock_memory_manager):
    mock_memory_manager.session_exists.return_value = False

    with pytest.raises(ChatNotFoundError):
        chat_service.reset_memory("nonexistent_chat_id")
