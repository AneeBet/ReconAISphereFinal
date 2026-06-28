from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.seed_users_repository import SeedUsersRepository
from app.services.seed_users_service import SeedUsersService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/seed-users")
def seed_users(
    db: Session = Depends(get_db)
):
    return SeedUsersService(
        SeedUsersRepository(db)
    ).seed()
