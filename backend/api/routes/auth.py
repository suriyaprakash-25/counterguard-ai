from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth")

MOCK_USER = {
    "id": "usr_123",
    "email": "investigator@counterguard.ai",
    "firstName": "Jane",
    "lastName": "Doe",
    "role": "Administrator",
    "organization": "Cyber Fraud Unit"
}

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    return {
        "data": {
            "user": MOCK_USER,
            "accessToken": "mock_access_token",
            "refreshToken": "mock_refresh_token"
        }
    }

@router.post("/logout")
def logout():
    return {"data": {"success": True}}

class RefreshRequest(BaseModel):
    refreshToken: str

@router.post("/refresh")
def refresh(request: RefreshRequest):
    return {
        "data": {
            "user": MOCK_USER,
            "accessToken": "new_mock_access_token",
            "refreshToken": "new_mock_refresh_token"
        }
    }

@router.get("/me")
def get_me():
    return {"data": MOCK_USER}
