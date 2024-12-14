import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.routes.websocket_routes import app

client = TestClient(app)


@pytest.mark.parametrize("endpoint", ["/check"])
def test_health_check(endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "OK"
    assert data["message"] == "Service is running correctly"
    assert data["version"] == "1.0.0"
    assert data["dependencies"]["memory_manager"] == "OK"
    assert data["dependencies"]["chat_service"] == "OK"


@pytest.mark.asyncio
async def test_websocket_chat_no_chat_id():
    async with client.websocket_connect("/chat/") as websocket:
        chat_id_message = await websocket.receive_text()
        assert "chat_id" in chat_id_message

        await websocket.send_text("Hello!")
        response = await websocket.receive_text()
        assert response


@pytest.mark.asyncio
async def test_websocket_chat_with_chat_id():
    chat_id = "mock_chat_id"
    async with client.websocket_connect(f"/chat/{chat_id}") as websocket:
        await websocket.send_text("Hello!")
        response = await websocket.receive_text()
        assert response


@pytest.mark.asyncio
async def test_websocket_chat_invalid_chat_id():
    invalid_chat_id = "nonexistent_chat_id"

    with pytest.raises(WebSocketDisconnect):
        async with client.websocket_connect(f"/chat/{invalid_chat_id}") as websocket:
            await websocket.send_text("Hello!")
