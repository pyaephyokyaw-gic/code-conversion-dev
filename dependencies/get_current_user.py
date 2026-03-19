from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from jose import jwt

from db.database import get_db
from models.user import User

security = HTTPBearer()
CLIENT_ID = "......"


async def get_current_user(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.cognito_id ==
                           "e7b4eaf8-d091-70ab-374a-bcc90a660643")
    )
    user = result.scalar_one_or_none()
    print("user:", vars(user))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: AsyncSession = Depends(get_db),
# ) -> User:
#     token = credentials.credentials

#     try:
#         key = await get_public_key(token)

#         if not key:
#             raise HTTPException(status_code=401, detail="Invalid token key")

#         payload = jwt.decode(
#             token,
#             key,
#             algorithms=["RS256"],
#             audience=CLIENT_ID,
#         )

#         cognito_sub = payload.get("sub")

#         if not cognito_sub:
#             raise HTTPException(
#                 status_code=401, detail="Invalid token payload")

#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#         )

#     # ✅ DB lookup (your system user)
#     result = await db.execute(
#         select(User).where(User.cognito_user_id == cognito_sub)
#     )
#     user = result.scalar_one_or_none()

#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return user
