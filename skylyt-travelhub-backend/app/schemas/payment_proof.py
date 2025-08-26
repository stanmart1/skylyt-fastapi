from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.payment_proof import ProofStatus


class PaymentProofCreate(BaseModel):
    transfer_reference: str
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class PaymentProofResponse(BaseModel):
    id: int
    payment_id: int
    transfer_reference: str
    file_path: str
    file_name: str
    file_size: Optional[int]
    mime_type: Optional[str]
    status: ProofStatus
    verification_notes: Optional[str]
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentProofVerification(BaseModel):
    status: ProofStatus
    verification_notes: Optional[str] = None