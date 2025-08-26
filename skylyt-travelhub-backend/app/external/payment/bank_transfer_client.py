from typing import Dict, Any, Optional
from decimal import Decimal
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class BankTransferClient:
    
    def __init__(self):
        self.payment_method = "bank_transfer"
    
    def create_transfer_request(self, amount: Decimal, currency: str = "USD", 
                              bank_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create bank transfer payment request"""
        try:
            transfer_ref = f"bt_{uuid.uuid4().hex[:12]}"
            
            # Use provided bank details
            if not bank_details:
                raise ValueError("Bank account details not configured")
            
            default_bank_details = bank_details.copy()
            default_bank_details["reference"] = transfer_ref
            
            transfer_data = {
                "transfer_reference": transfer_ref,
                "amount": str(amount),
                "currency": currency,
                "bank_details": bank_details or default_bank_details,
                "status": "pending_payment",
                "instructions": [
                    f"Transfer {amount} {currency} to the account details provided",
                    f"Use reference: {transfer_ref}",
                    "Upload proof of payment after transfer",
                    "Payment will be verified within 24 hours"
                ],
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created bank transfer request: {transfer_ref}")
            return {
                "status": "success",
                "data": transfer_data
            }
            
        except Exception as e:
            logger.error(f"Bank transfer request creation failed: {e}")
            raise
    
    def upload_proof_of_payment(self, transfer_reference: str, 
                               proof_file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload proof of payment for bank transfer"""
        try:
            proof_id = f"proof_{uuid.uuid4().hex[:8]}"
            
            proof_data = {
                "proof_id": proof_id,
                "transfer_reference": transfer_reference,
                "file_path": proof_file_path,
                "upload_time": datetime.utcnow().isoformat(),
                "status": "uploaded",
                "metadata": metadata or {},
                "verification_status": "pending_verification"
            }
            
            logger.info(f"Uploaded proof of payment: {proof_id} for transfer: {transfer_reference}")
            return {
                "status": "success",
                "data": proof_data
            }
            
        except Exception as e:
            logger.error(f"Proof upload failed: {e}")
            raise
    
    def verify_payment(self, transfer_reference: str, admin_notes: str = None) -> Dict[str, Any]:
        """Verify bank transfer payment (admin function)"""
        try:
            verification_data = {
                "transfer_reference": transfer_reference,
                "verification_status": "verified",
                "verified_at": datetime.utcnow().isoformat(),
                "admin_notes": admin_notes,
                "payment_status": "completed"
            }
            
            logger.info(f"Verified bank transfer: {transfer_reference}")
            return {
                "status": "success",
                "data": verification_data
            }
            
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            raise
    
    def reject_payment(self, transfer_reference: str, reason: str) -> Dict[str, Any]:
        """Reject bank transfer payment (admin function)"""
        try:
            rejection_data = {
                "transfer_reference": transfer_reference,
                "verification_status": "rejected",
                "rejected_at": datetime.utcnow().isoformat(),
                "rejection_reason": reason,
                "payment_status": "failed"
            }
            
            logger.info(f"Rejected bank transfer: {transfer_reference}")
            return {
                "status": "success",
                "data": rejection_data
            }
            
        except Exception as e:
            logger.error(f"Payment rejection failed: {e}")
            raise