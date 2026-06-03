from typing import Any, Dict
from jose import jwt
from app.core.config import settings

def verify_token(token: str) -> Dict[str, Any]:
    try:
        # Supabase signs JWTs with HS256 using the JWT Secret
        payload = jwt.decode(
            token, 
            settings.supabase_jwt_secret, 
            algorithms=["HS256"],
            options={"verify_aud": False} # Sometimes audience varies, we can disable or verify it
        )
        return payload
    except jwt.JWTError:
        return None
