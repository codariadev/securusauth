from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.app.security import create_access_token, verify_password
import bcrypt

router = APIRouter(tags=["Auth"])

HASH_SECRET123 = bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode("utf-8")

fake_users_db = {
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": HASH_SECRET123,
    }
}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if not user or not verify_password(
        form_data.password, user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}