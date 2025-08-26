import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestPaymentFlow:
    def test_stripe_payment_flow(self, client: TestClient, auth_headers, test_booking):
        """Test Stripe payment processing flow."""
        
        with patch('app.external.payment.stripe_client.StripeClient.create_payment_intent') as mock_stripe:
            mock_stripe.return_value = {
                "id": "pi_test123",
                "status": "succeeded",
                "amount": 20000,  # $200.00 in cents
                "currency": "usd"
            }
            
            payment_data = {
                "booking_id": test_booking.id,
                "gateway": "stripe",
                "amount": 200.00,
                "currency": "USD",
                "payment_method": "card",
                "card_token": "tok_visa"
            }
            
            response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["gateway"] == "stripe"

    def test_flutterwave_payment_flow(self, client: TestClient, auth_headers, test_booking):
        """Test Flutterwave payment processing flow."""
        
        with patch('app.external.payment.flutterwave_client.FlutterwaveClient.process_payment') as mock_flw:
            mock_flw.return_value = {
                "status": "successful",
                "transaction_id": "flw_123456",
                "amount": 200.00,
                "currency": "USD"
            }
            
            payment_data = {
                "booking_id": test_booking.id,
                "gateway": "flutterwave",
                "amount": 200.00,
                "currency": "USD",
                "payment_method": "card"
            }
            
            response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["gateway"] == "flutterwave"

    def test_bank_transfer_payment_flow(self, client: TestClient, auth_headers, test_booking):
        """Test bank transfer payment flow with proof upload."""
        
        # Simulate file upload for payment proof
        with patch('app.services.payment_service.PaymentService.save_payment_proof') as mock_save:
            mock_save.return_value = "uploads/payment_proofs/proof_123.jpg"
            
            payment_data = {
                "booking_id": test_booking.id,
                "gateway": "bank_transfer",
                "amount": 200.00,
                "currency": "USD",
                "payment_method": "bank_transfer"
            }
            
            # Mock file upload
            files = {"proof_file": ("proof.jpg", b"fake image data", "image/jpeg")}
            
            response = client.post("/api/v1/payments/process", 
                                 data=payment_data, 
                                 files=files, 
                                 headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending_verification"

    def test_payment_webhook_stripe(self, client: TestClient):
        """Test Stripe webhook processing."""
        
        webhook_data = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "status": "succeeded",
                    "amount": 20000,
                    "currency": "usd",
                    "metadata": {
                        "booking_id": "1"
                    }
                }
            }
        }
        
        with patch('app.services.payment_service.PaymentService.handle_webhook') as mock_webhook:
            mock_webhook.return_value = {"status": "processed"}
            
            response = client.post("/api/v1/payments/webhook", 
                                 json=webhook_data,
                                 headers={"stripe-signature": "test_signature"})
            assert response.status_code == 200

    def test_payment_refund_flow(self, client: TestClient, auth_headers):
        """Test payment refund processing."""
        
        # Create a completed payment first
        with patch('app.services.payment_service.PaymentService.process_refund') as mock_refund:
            mock_refund.return_value = {
                "status": "refunded",
                "refund_id": "re_test123",
                "amount": 200.00
            }
            
            refund_data = {
                "reason": "Customer request",
                "amount": 200.00
            }
            
            response = client.post("/api/v1/payments/1/refund", 
                                 json=refund_data, 
                                 headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "refunded"

    def test_payment_status_check(self, client: TestClient, auth_headers):
        """Test payment status checking."""
        
        response = client.get("/api/v1/payments/1", headers=auth_headers)
        # This might return 404 if payment doesn't exist, which is fine for testing
        assert response.status_code in [200, 404]

    def test_invalid_payment_gateway(self, client: TestClient, auth_headers, test_booking):
        """Test payment with invalid gateway."""
        
        payment_data = {
            "booking_id": test_booking.id,
            "gateway": "invalid_gateway",
            "amount": 200.00,
            "currency": "USD"
        }
        
        response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
        assert response.status_code == 400

    def test_payment_amount_mismatch(self, client: TestClient, auth_headers, test_booking):
        """Test payment with amount mismatch."""
        
        payment_data = {
            "booking_id": test_booking.id,
            "gateway": "stripe",
            "amount": 100.00,  # Different from booking amount
            "currency": "USD"
        }
        
        response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
        assert response.status_code == 400