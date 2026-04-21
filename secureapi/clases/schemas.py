from typing import Any, Literal

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="usuario_comun", min_length=3, max_length=50)


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
    role: str


class UserListItemResponse(UserResponse):
    created_at: str | None = None


class UserListResponse(BaseModel):
    users: list[UserListItemResponse]


class RoleUpdateRequest(BaseModel):
    role: str = Field(min_length=3, max_length=50)


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    description: str = Field(default="", max_length=200)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str = ""


class RoleListResponse(BaseModel):
    roles: list[RoleResponse]


class MessageResponse(BaseModel):
    message: str


class UserInactiveResponse(MessageResponse):
    username: str


class MilestoneIssueCreateRequest(BaseModel):
    milestone: str = Field(min_length=2, max_length=120)
    issue_type: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=300)


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=600)
    milestone: str = Field(default="", max_length=120)
    issue_type: str = Field(default="general", max_length=80)
    milestone_issue_id: int | None = None
    assigned_to_username: str = Field(min_length=3, max_length=50)
    due_at: str = Field(description="Formato recomendado: YYYY-MM-DD HH:MM:SS")


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["no_iniciada", "en_proceso", "cumplida"]
    notes: str = Field(default="", max_length=600)


class TaskCreatedResponse(BaseModel):
    id: int
    title: str
    assigned_to: str
    status: str
    due_at: str


class TaskStatusUpdatedResponse(MessageResponse):
    task_id: int
    status: str


class TaskInactiveResponse(MessageResponse):
    task_id: int


class MilestoneIssueResponse(BaseModel):
    id: int
    milestone: str
    issue_type: str
    description: str = ""


class MilestoneIssueListResponse(BaseModel):
    items: list[MilestoneIssueResponse]


class TaskBoardItemResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    milestone: str | None = None
    issue_type: str | None = None
    status: str
    due_at: str | None = None
    progress_notes: str | None = None
    completion_notes: str | None = None
    completed_at: str | None = None
    created_at: str | None = None
    milestone_issue_id: int | None = None
    catalog_milestone: str | None = None
    catalog_issue_type: str | None = None
    assigned_to: str | None = None
    assigned_role: str | None = None
    created_by: str | None = None
    created_by_role: str | None = None


class TaskListResponse(BaseModel):
    tasks: list[TaskBoardItemResponse]


class HashResponse(BaseModel):
    hash: str


class ScanResponse(BaseModel):
    url: str
    usuario: str | None = None
    endpoints_encontrados: Any
    cabeceras: Any
    seguridad_https: str
    nivel_riesgo: str
    vulnerabilidades_detectadas: list[str]


class ScanHistoryRecordResponse(BaseModel):
    id: int
    url: str | None = None
    endpoints: Any | None = None
    headers: Any | None = None
    https_status: str | None = None
    risk: str | None = None
    fecha: str | None = None
    performed_by: int | None = None
    performed_by_username: str | None = None
    active: int | None = None


class ScanHistoryResponse(BaseModel):
    registros: list[ScanHistoryRecordResponse]
