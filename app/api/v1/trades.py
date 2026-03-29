from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.trade import Trade
from app.models.user import User
from app.schemas.trade import TradeCreate, TradeListOut, TradeOut, TradeUpdate

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post(
    "/",
    response_model=TradeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trade",
)
def create_trade(
    payload: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trade = Trade(**payload.model_dump(), owner_id=current_user.id)
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


@router.get("/", response_model=TradeListOut, summary="List my trades")
def list_my_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Trade).filter(Trade.owner_id == current_user.id)
    if status_filter:
        query = query.filter(Trade.status == status_filter)
    total = query.count()
    trades = query.order_by(Trade.created_at.desc()).offset(skip).limit(limit).all()
    return TradeListOut(total=total, trades=trades)


@router.get(
    "/all",
    response_model=TradeListOut,
    summary="[Admin] List all trades across all users",
    dependencies=[Depends(require_admin)],
)
def list_all_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    total = db.query(Trade).count()
    trades = db.query(Trade).order_by(Trade.created_at.desc()).offset(skip).limit(limit).all()
    return TradeListOut(total=total, trades=trades)


@router.get("/{trade_id}", response_model=TradeOut, summary="Get trade by ID")
def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return trade


@router.patch("/{trade_id}", response_model=TradeOut, summary="Update a trade")
def update_trade(
    trade_id: int,
    payload: TradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trade, field, value)

    db.commit()
    db.refresh(trade)
    return trade


@router.delete(
    "/{trade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trade",
)
def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")
    db.delete(trade)
    db.commit()
