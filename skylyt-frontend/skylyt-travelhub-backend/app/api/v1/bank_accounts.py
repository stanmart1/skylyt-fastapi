from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import Settings

router = APIRouter(prefix="/bank-accounts", tags=["bank-accounts"])

@router.get("")
def get_bank_accounts(db: Session = Depends(get_db)):
    """Get bank account details for transfers"""
    settings = db.query(Settings).filter(Settings.is_primary_account == True).first()
    
    if not settings or not settings.bank_name:
        raise HTTPException(status_code=404, detail="Bank account details not configured")
    
    return {
        "bank_name": settings.bank_name,
        "account_number": settings.account_number,
        "account_name": settings.account_name
    }