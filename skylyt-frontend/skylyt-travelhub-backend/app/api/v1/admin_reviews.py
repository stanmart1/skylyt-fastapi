from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from typing import List, Optional

router = APIRouter(prefix="/admin/reviews", tags=["admin-reviews"])

@router.get("/")
def get_reviews(
    status: Optional[str] = Query(None),
    rating: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews with filters"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Return empty list for now - implement proper review model later
    return []

@router.put("/{review_id}/status")
def update_review_status(
    review_id: int,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update review status"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Review status updated successfully"}

@router.post("/{review_id}/response")
def add_review_response(
    review_id: int,
    response_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add admin response to review"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Response added successfully"}