from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from ..services.conversion_service import get_conversion_results_service
from dependencies.get_current_user import get_current_user

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("/")
async def get_conversion_results(
        limit: int = Query(10, le=100),
        offset: int = Query(0),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    data = await get_conversion_results_service(limit, offset, user, db)
    return data
