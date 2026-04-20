from typing import Literal

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class MasterTokenRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in_minutes: int


class UserResponse(BaseModel):
    id: int
    username: str
    role: Literal["super_admin", "supervisor", "usuario"]


class RoleUpdateRequest(BaseModel):
    role: Literal["super_admin", "supervisor", "usuario"]


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=600)
    milestone: str = Field(default="", max_length=120)
    issue_type: str = Field(default="general", max_length=80)
    assigned_to_username: str = Field(min_length=3, max_length=50)
    due_at: str = Field(description="Formato recomendado: YYYY-MM-DD HH:MM:SS")


class TaskCompleteRequest(BaseModel):
    completion_notes: str = Field(min_length=3, max_length=600)
