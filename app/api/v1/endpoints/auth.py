from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from jose import jwt
import uuid
import time

router = APIRouter()

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Mock login endpoint for Swagger UI testing.
    In production, user authentication is handled by the Supabase Frontend Auth.
    This endpoint generates a valid Supabase JWT token based on the provided username.
    """
    
    # Generate a deterministic UUID based on the username for testing
    user_id = str(uuid.uuid5(uuid.NAMESPACE_OID, form_data.username))
    
    payload = {
        "sub": user_id,
        "email": form_data.username,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600 * 24 * 7, # 7 days
        "iat": int(time.time()),
    }
    
    token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer"}
