from pydantic import BaseModel


class ChatResponseDTO(BaseModel):
    request_id: str
    response: str
