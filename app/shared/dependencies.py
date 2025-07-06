from fastapi import Request, HTTPException, status
from models import User
from .types import UserSessionData, Role

async def get_current_user(request: Request) -> User:
    user_campus_id = request.session.get('campus_id')
    if user_campus_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if not isinstance(user_campus_id, str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    user = await User.find_one(User.campus_id == user_campus_id)
    if user is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    request.session.update(UserSessionData(**user.model_dump()).model_dump())
    return user


async def get_admin_user(request: Request) -> User:
    """Get current user and verify they have admin or manager role"""
    user = await get_current_user(request)
    if Role.ADMIN not in user.roles and Role.MANAGER not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You got no permission to do it!"
        )
    return user

async def get_admin_role_user(request: Request) -> User:
    user = await get_current_user(request)
    if Role.ADMIN not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You got no permission to do it!"
        )
    return user