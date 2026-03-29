from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserOut],
    summary="[Admin] List all users",
    dependencies=[Depends(require_admin)],
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="[Admin] Get user by ID",
    dependencies=[Depends(require_admin)],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserOut,
    summary="[Admin] Update user role",
    dependencies=[Depends(require_admin)],
)
def update_role(user_id: int, payload: UserRoleUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserOut,
    summary="[Admin] Deactivate a user account",
    dependencies=[Depends(require_admin)],
)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
