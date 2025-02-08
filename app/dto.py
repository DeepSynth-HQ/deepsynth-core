from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LoginRequest(BaseModel):
    email: str = Field(..., description="The email", example="john_doe@example.com")
    password: str = Field(..., description="The password", example="password123")


class SignupRequest(BaseModel):
    username: str = Field(..., description="The username", example="john_doe")
    email: str = Field(..., description="The email", example="john_doe@example.com")
    password: Optional[str] = Field(
        None, description="The password", example="password123"
    )
    avatar: Optional[str] = Field(
        None, description="The avatar", example="https://avatar.iran.liara.run/public"
    )


class AgentCallRequest(BaseModel):
    message: str = Field(
        ...,
        description="The message to send to the agent",
        example="Hello, how are you?",
    )
    session_id: str = Field(..., description="The session id", example="s-1234567890")
    images: list[str] = Field(
        [],
        description="The images to send to the agent",
        examples=[
            [
                "https://platsbucketdev.s3.ap-southeast-1.amazonaws.com/BTCUSDT_2025-01-19_15-30-42.png"
            ]
        ],
    )


class AgentHistoryRequest(BaseModel):
    session_id: Optional[str] = Field(
        None, description="The session id", example="s-1234567890"
    )


class FileResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    extension: str
    storage_provider: str
    is_public: bool
    user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserRequestDTO(BaseModel):
    username: str = Field(..., description="The username", example="john_doe")
    email: str = Field(..., description="The email", example="john_doe@example.com")


class UserResponseDTO(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime]


class WalletRequestDTO(BaseModel):
    user_id: str


class WalletResponseDTO(BaseModel):
    id: int
    user_id: int
    public_key: str
    private_key: str
    seed_phrase: str


class SocialCallbackRequest(BaseModel):
    username: str = Field(..., description="The username", example="odin")
    email: str = Field(..., description="The email", example="odin@example.com")
    avatar: Optional[str] = Field(
        None, description="The avatar", example="https://avatar.iran.liara.run/public"
    )
    ref_code: Optional[str] = Field(
        None, description="The ref code", example="sjk2ioIi"
    )


class UseRefCodeRequest(BaseModel):
    ref_code: str


class LoginXRequest(BaseModel):
    token: str
    ref_code: Optional[str] = Field(
        None, description="The ref code", example="sjk2ioIi"
    )
