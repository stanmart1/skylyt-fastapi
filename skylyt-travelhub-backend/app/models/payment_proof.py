from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, DateTime, Text
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class ProofStatus(enum.Enum):
    UPLOADED = "uploaded"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"


class PaymentProof(BaseModel):
    __tablename__ = "payment_proofs"
    
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    transfer_reference = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    status = Column(SQLEnum(ProofStatus), default=ProofStatus.UPLOADED, nullable=False)
    verification_notes = Column(Text, nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="proofs")
    verified_by_user = relationship("User", foreign_keys=[verified_by])