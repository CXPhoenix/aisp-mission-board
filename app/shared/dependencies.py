from fastapi import Request, HTTPException, status
from models import User
from .types import UserSessionData

async def get_current_user(request: Request) -> User:
    user_campus_id = request.session.get('campus_id')
    if user_campus_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if isinstance(user_campus_id, str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    user = await User.find_one(User.campus_id == user_campus_id)
    if user is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    request.session.update(UserSessionData(**user.model_dump()).model_dump())
    return user

