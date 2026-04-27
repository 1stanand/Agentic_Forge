from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    display_name: str
    user_id: int
    is_admin: bool


# Chat
class ChatMessage(BaseModel):
    role: str
    content: str
    context_type: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    context_type: str
    session_title: str


class ChatSession(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatSessionDetail(BaseModel):
    id: str
    title: str
    messages: List[ChatMessage]


# Generation
class GenerateRequest(BaseModel):
    jira_input_mode: str
    jira_story_id: Optional[str] = None
    jira_csv_raw: Optional[str] = None
    flow_type: str
    three_amigos_notes: str = ""
    module: str = "cas"
    jira_pat_override: Optional[str] = None


class GenerateResponse(BaseModel):
    job_id: str


class GenerateStreamEvent(BaseModel):
    agent: Optional[int] = None
    elapsed: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None


class GenerateResult(BaseModel):
    job_id: str
    feature_file: str
    gap_report: Dict[str, Any]
    confidence_score: float


class GenerateRunning(BaseModel):
    status: str
    current_agent: int
    elapsed: int


# Settings
class SettingsRequest(BaseModel):
    jira_url: Optional[str] = None
    jira_pat: Optional[str] = None


class SettingsResponse(BaseModel):
    jira_url: Optional[str] = None
    jira_pat: Optional[str] = None
    display_name: str
    theme_pref: str


class ProfileUpdateRequest(BaseModel):
    display_name: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class TestJiraResponse(BaseModel):
    status: str
    message: str


class TestModelResponse(BaseModel):
    status: str
    message: str
    response_length: Optional[int] = None


# Admin
class CreateUserRequest(BaseModel):
    username: str
    display_name: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    created_at: datetime


class UserListItem(BaseModel):
    id: int
    username: str
    display_name: str
    is_active: bool
    last_login: Optional[datetime] = None
