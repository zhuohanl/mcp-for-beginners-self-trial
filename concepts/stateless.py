from fastapi import FastAPI, Body, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

# Secret key for JWT encoding (use a secure random key in production)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashed123456",
        "is_admin": False,
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashed222222",
        "is_admin": True,
        "disabled": False,
    },
}

security = HTTPBearer()

fake_pets_db = {
    1: {"id": 1, "name": "Buddy", "type": "dog", "require_admin": False},
    2: {"id": 2, "name": "Whiskers", "type": "cat", "require_admin": True},
    3: {"id": 3, "name": "Charlie", "type": "bird", "require_admin": False},
}

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/login")
def login(request: dict=Body(...)):
    username = request.get("username")
    password = request.get("password")
    
    user_dict = fake_users_db.get(username)
    if not user_dict or user_dict["hashed_password"] != f"fakehashed{password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with additional user information
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": username,
            "is_admin": user_dict["is_admin"],
            "full_name": user_dict["full_name"],
            "email": user_dict["email"]
        }, 
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/pets/{pet_id}")
def get_pet(pet_id: int, current_user: dict = Depends(verify_token)):
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
        "requested_by": current_user.get("sub"),
        "is_admin": current_user.get("is_admin", False)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)