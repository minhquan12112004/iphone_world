from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # Note: Not used for Supabase login, but used for swagger UI

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    email = payload.get("email") # Supabase JWT often includes email
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    # Query user from local db
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    # Auto-create user if they log in via Supabase but don't exist locally
    if not user:
        user = User(id=user_id, email=email or "unknown@supabase.com", name="Supabase User")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
    return user
