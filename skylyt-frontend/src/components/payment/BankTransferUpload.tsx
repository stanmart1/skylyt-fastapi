import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Building2, Upload, FileText } from 'lucide-react';
import { usePayment } from '@/hooks/usePayment';

interface BankTransferUploadProps {
  amount: number;
  currency: string;
  bookingId: number;
  onSuccess: (payment: any) => void;
  onError: (error: string) => void;
}

export const BankTransferUpload = ({ 
  amount, 
  currency, 
  bookingId, 
  onSuccess, 
  onError 
}: BankTransferUploadProps) => {
  const [transferData, setTransferData] = useState({
    referenceNumber: '',
    transferDate: '',
    notes: '',
  });
  const [proofFile, setProofFile] = useState<File | null>(null);
  const [bankDetails, setBankDetails] = useState({
    bank_name: 'Loading...',
    account_name: 'Loading...',
    account_number: 'Loading...'
  });
  
  const { isProcessing, processPayment } = usePayment();

  useEffect(() => {
    const fetchBankDetails = async () => {
      try {
        const { apiService } = await import('@/services/api');
        const details = await apiService.request('/payments/bank-account-details');
        setBankDetails(details);
      } catch (error) {
        onError('Bank account details not configured. Please contact administrator.');
      }
    };
    fetchBankDetails();
  }, []);

  const handleInputChange = (field: string, value: string) => {
    setTransferData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProofFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!proofFile) {
      onError('Please upload proof of payment');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('booking_id', String(bookingId));
      formData.append('gateway', 'bank_transfer');
      formData.append('amount', String(amount));
      formData.append('currency', currency);
      formData.append('payment_method', 'bank_transfer');
      formData.append('reference_number', transferData.referenceNumber);
      formData.append('transfer_date', transferData.transferDate);
      formData.append('notes', transferData.notes);
      formData.append('proof_file', proofFile);

      // Note: This would need a special API endpoint for file uploads
      const result = await processPayment({
        booking_id: bookingId,
        gateway: 'bank_transfer',
        amount,
        currency,
        payment_method: 'bank_transfer',
        reference_number: transferData.referenceNumber,
        transfer_date: transferData.transferDate,
        notes: transferData.notes,
      });
      
      onSuccess(result);
    } catch (error) {
      onError('Failed to submit bank transfer proof. Please try again.');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5" />
          Bank Transfer
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Bank Details */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Bank Transfer Details</h4>
            <div className="text-sm space-y-1">
              <p><strong>Bank:</strong> {bankDetails.bank_name}</p>
              <p><strong>Account Name:</strong> {bankDetails.account_name}</p>
              <p><strong>Account Number:</strong> {bankDetails.account_number}</p>
              <p><strong>Amount:</strong> {currency} {amount}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="referenceNumber">Transfer Reference Number</Label>
              <Input
                id="referenceNumber"
                value={transferData.referenceNumber}
                onChange={(e) => handleInputChange('referenceNumber', e.target.value)}
                placeholder="Enter transfer reference"
                required
              />
            </div>

            <div>
              <Label htmlFor="transferDate">Transfer Date</Label>
              <Input
                id="transferDate"
                type="date"
                value={transferData.transferDate}
                onChange={(e) => handleInputChange('transferDate', e.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="proofFile">Upload Proof of Payment</Label>
              <Input
                id="proofFile"
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileChange}
                required
              />
              <p className="text-xs text-gray-600 mt-1">
                Upload receipt, screenshot, or bank statement (JPG, PNG, PDF)
              </p>
            </div>

            <div>
              <Label htmlFor="notes">Additional Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={transferData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Any additional information..."
                rows={3}
              />
            </div>

            {proofFile && (
              <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                <FileText className="h-4 w-4" />
                <span className="text-sm">{proofFile.name}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={isProcessing}
              className="w-full bg-gray-600 hover:bg-gray-700"
            >
              {isProcessing ? 'Submitting...' : 'Submit Payment Proof'}
            </Button>
          </form>

          <div className="text-xs text-gray-600">
            <p>Your payment will be verified within 24 hours. You will receive a confirmation email once verified.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};