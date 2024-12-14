from typing import Literal

from pydantic import BaseModel


class ErrorResponseDTO(BaseModel):
    status: Literal["error", "success"]
    code: int
    error: str
    message: str
