from fastapi import APIRouter, Depends
from shared.dependencies import get_admin_user
from . import index, mall, mission, review, user

router = APIRouter(prefix="/management", dependencies=[Depends(get_admin_user)])

router.include_router(index.router)
router.include_router(mall.router)
router.include_router(mall.physical_router)
router.include_router(mission.router)
router.include_router(review.router)
router.include_router(user.router)
