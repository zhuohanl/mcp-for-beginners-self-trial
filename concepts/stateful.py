from fastapi import FastAPI, Body, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

class User(BaseModel):
    username: str
    full_name: str
    email: str
    hashed_password: str
    is_admin: bool = False
    disabled: bool = False
    logged_in: bool = False

fake_users_db = {
    "johndoe": User(
        username="johndoe",
        full_name="John Doe",
        email="johndoe@example.com",
        hashed_password="fakehashed123456",
        is_admin=False,
        disabled=False
    ),
    "alice": User(
        username="alice",
        full_name="Alice Wonderson",
        email="alice@example.com",
        hashed_password="fakehashed222222",
        is_admin=True,
        disabled=False
    ),
}

fake_pets_db = {
    1: {"id": 1, "name": "Buddy", "type": "dog", "require_admin": False},
    2: {"id": 2, "name": "Whiskers", "type": "cat", "require_admin": True},
    3: {"id": 3, "name": "Charlie", "type": "bird", "require_admin": False},
}

security = APIKeyHeader(name="X-Session-ID", description="Session ID from login")

# Session storage for stateful authentication
active_sessions = {}

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class SessionResponse(BaseModel):
    session_id: str
    message: str

def verify_session(session_id: str = Depends(security)):
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )
    
    session_data = active_sessions[session_id]
    user_data = session_data["user_data"]
    
    return {
        "session_id": session_id,
        "username": session_data["username"],
        "is_admin": user_data.is_admin,
        "full_name": user_data.full_name,
        "email": user_data.email
    }

@app.post("/login")
def login(request: dict=Body(...)):
    username = request.get("username")
    password = request.get("password")
    
    user = fake_users_db.get(username)
    if not user or user.hashed_password != f"fakehashed{password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is already logged in
    if user.logged_in:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User '{username}' is already logged in. Please logout first."
        )
    
    # Set user as logged in
    user.logged_in = True
    
    # Create a new session
    session_id = str(uuid.uuid4())
    session_data = {
        "username": username,
        "created_at": datetime.now(timezone.utc),
        "user_data": user
    }
    active_sessions[session_id] = session_data
    
    return SessionResponse(session_id=session_id, message="Login successful")

@app.post("/logout")
def logout(current_user: dict = Depends(verify_session)):
    session_id = current_user.get("session_id")
    username = current_user.get("username")
    
    if session_id and session_id in active_sessions:
        del active_sessions[session_id]
    
    # Set user logged_in flag to False
    user = fake_users_db.get(username)
    if user:
        user.logged_in = False
    
    return {"message": "Successfully logged out"}

@app.get("/sessions")
def get_active_sessions(current_user: dict = Depends(verify_session)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": sid,
                "username": data["username"],
                "created_at": data["created_at"],
                "logged_in": data["user_data"].logged_in
            }
            for sid, data in active_sessions.items()
        ]
    }

@app.get("/pets/{pet_id}")
def get_pet(pet_id: int, current_user: dict = Depends(verify_session)):
    pet = fake_pets_db.get(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.get("require_admin") and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this pet"
        )

    return {
        "pet": pet,
        "requested_by": current_user.get("username"),
        "is_admin": current_user.get("is_admin", False)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)