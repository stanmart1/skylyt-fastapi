import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CreditCard, ArrowLeft, CheckCircle, XCircle, Upload, Copy, Building2 } from 'lucide-react';
import Navigation from '@/components/Navigation';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

const Payment = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { currency } = useCurrency();
  
  const bookingId = searchParams.get('bookingId');
  const amount = searchParams.get('amount');
  const method = searchParams.get('method') || 'stripe';
  
  const [loading, setLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState('pending');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [transactionRef, setTransactionRef] = useState('');
  const [bankDetails, setBankDetails] = useState<any>(null);
  const [loadingBankDetails, setLoadingBankDetails] = useState(false);
  
  useEffect(() => {
    // Generate transaction reference
    if (bookingId) {
      setTransactionRef(`SKY-${bookingId}-${Date.now().toString().slice(-6)}`);
    }
    
    // Fetch bank details if bank transfer
    if (method === 'bank_transfer') {
      fetchBankDetails();
    }
  }, [bookingId, method]);
  
  const fetchBankDetails = async () => {
    setLoadingBankDetails(true);
    try {
      const response = await apiService.request('/bank-accounts');
      setBankDetails(response);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load bank account details",
        variant: "destructive"
      });
    } finally {
      setLoadingBankDetails(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied!",
      description: "Text copied to clipboard",
    });
  };

  const handlePayment = async () => {
    if (!bookingId) {
      toast({
        title: "Error",
        description: "No booking ID provided",
        variant: "destructive"
      });
      return;
    }
    
    if (method === 'bank_transfer' && !selectedFile) {
      toast({
        title: "Upload Required",
        description: "Please upload proof of payment",
        variant: "destructive"
      });
      return;
    }
    
    console.log('Processing payment for booking ID:', bookingId);
    setLoading(true);
    try {
      if (method === 'bank_transfer' && selectedFile) {
        // Upload proof of payment for bank transfer
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('booking_id', bookingId);
        formData.append('payment_reference', transactionRef);
        
        console.log('Uploading proof for booking:', bookingId);
        const response = await fetch('https://skylytapi.scaleitpro.com/api/v1/payments/upload-proof', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Upload failed:', errorText);
          throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
        
        setPaymentStatus('pending_verification');
      } else {
        // Initialize payment for other methods
        const result = await apiService.request('/payments/initialize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            booking_id: parseInt(bookingId),
            payment_method: method,
            payment_reference: transactionRef
          })
        });
        
        // Simulate payment completion for other methods
        setTimeout(() => {
          setPaymentStatus('completed');
        }, 2000);
      }
      
      setLoading(false);
      
    } catch (error) {
      console.error('Payment error:', error);
      setLoading(false);
      setPaymentStatus('failed');
      toast({
        title: "Payment Failed",
        description: error instanceof Error ? error.message : "Please try again.",
        variant: "destructive"
      });
    }
  };

  if (paymentStatus === 'completed' || paymentStatus === 'pending_verification') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <Card className="max-w-md mx-auto text-center">
            <CardContent className="p-8">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">
                {paymentStatus === 'completed' ? 'Payment Successful!' : 'Booking Completed!'}
              </h2>
              <p className="text-gray-600 mb-6">
                {paymentStatus === 'completed' 
                  ? 'Your booking has been confirmed.' 
                  : 'Your payment proof has been submitted. We will verify your payment and confirm your booking within 24 hours.'}
              </p>
              <div className="space-y-3">
                <Button onClick={() => navigate('/dashboard')} className="w-full">
                  View My Bookings
                </Button>
                <Button onClick={() => navigate('/')} variant="outline" className="w-full">
                  Return to Home
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'failed') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <Card className="max-w-md mx-auto text-center">
            <CardContent className="p-8">
              <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Payment Failed</h2>
              <p className="text-gray-600 mb-6">Please try again or use a different payment method.</p>
              <Button onClick={() => navigate(-1)} className="w-full">
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="ghost" 
          onClick={() => navigate(-1)}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <Card className="max-w-lg mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Complete Payment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {method === 'bank_transfer' ? (
              <>
                {/* Bank Account Details Section */}
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Building2 className="h-5 w-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-900">Bank Account Details</h3>
                  </div>
                  {loadingBankDetails ? (
                    <div className="flex justify-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    </div>
                  ) : bankDetails ? (
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Bank Name:</span>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{bankDetails.bank_name}</span>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            onClick={() => copyToClipboard(bankDetails.bank_name)}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Account Number:</span>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{bankDetails.account_number}</span>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            onClick={() => copyToClipboard(bankDetails.account_number)}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Account Name:</span>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{bankDetails.account_name}</span>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            onClick={() => copyToClipboard(bankDetails.account_name)}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Amount:</span>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg text-blue-600">
                            <PriceDisplay amount={parseFloat(amount || '0')} currency={currency} />
                          </span>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            onClick={() => copyToClipboard(amount || '')}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-red-600 text-sm">Failed to load bank account details</p>
                  )}
                </div>

                {/* Instructions Section */}
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <h4 className="font-semibold text-yellow-800 mb-2">Transfer Instructions</h4>
                  <p className="text-sm text-yellow-700 mb-3">
                    Transfer the exact amount to the bank account above. Use{' '}
                    <span className="font-bold">{transactionRef}</span> as the transaction reference when transferring.
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-yellow-700">Transaction Reference:</span>
                    <code className="bg-yellow-100 px-2 py-1 rounded text-sm font-mono">{transactionRef}</code>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => copyToClipboard(transactionRef)}
                      className="h-6 w-6 p-0"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                  <p className="text-xs text-yellow-600 mt-2">
                    Upload proof of payment below to complete your booking.
                  </p>
                </div>

                {/* Upload Proof Section */}
                <div className="space-y-4">
                  <h4 className="font-semibold">Upload Proof of Payment</h4>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <input
                      type="file"
                      id="proof-upload"
                      accept="image/*,.pdf"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <Button 
                      variant="outline" 
                      className="mb-2"
                      onClick={() => document.getElementById('proof-upload')?.click()}
                      type="button"
                    >
                      Choose File
                    </Button>
                    <p className="text-sm text-gray-500">
                      {selectedFile ? selectedFile.name : 'Upload receipt, screenshot, or PDF'}
                    </p>
                  </div>
                </div>

                <Button 
                  onClick={handlePayment}
                  disabled={loading || !selectedFile}
                  className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700"
                >
                  {loading ? 'Processing...' : 'Complete Payment'}
                </Button>
              </>
            ) : (
              <>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    <PriceDisplay amount={parseFloat(amount || '0')} currency={currency} />
                  </div>
                  <p className="text-gray-600">Total Amount</p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Payment Method</p>
                  <p className="font-semibold capitalize">{method}</p>
                </div>

                <Button 
                  onClick={handlePayment}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700"
                >
                  {loading ? 'Processing...' : `Pay with ${method}`}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Payment;