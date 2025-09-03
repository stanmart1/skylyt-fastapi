import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Clock, Home, FileText } from 'lucide-react';
import Navigation from '@/components/Navigation';

const PaymentConfirmation = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const bookingId = searchParams.get('bookingId');
  const status = searchParams.get('status');

  useEffect(() => {
    // Redirect to home if no booking ID
    if (!bookingId) {
      navigate('/');
    }
  }, [bookingId, navigate]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Payment Completed
              </h1>
              <p className="text-xl text-gray-600">
                Awaiting Approval
              </p>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mb-6">
              <div className="flex items-center justify-center gap-2 mb-3">
                <Clock className="h-5 w-5 text-blue-600" />
                <span className="font-semibold text-blue-900">What happens next?</span>
              </div>
              <div className="text-sm text-blue-800 space-y-2">
                <p>✓ Your payment proof has been submitted successfully</p>
                <p>✓ Our team will verify your payment within 24 hours</p>
                <p>✓ You'll receive an email confirmation once approved</p>
                <p>✓ Your booking will be confirmed after verification</p>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-6">
              <p className="text-sm text-gray-600 mb-2">Booking Reference</p>
              <p className="font-mono text-lg font-semibold text-gray-900">
                SKY-{bookingId}
              </p>
            </div>

            <div className="space-y-3">
              <Button 
                onClick={() => navigate('/dashboard')} 
                className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700"
              >
                <FileText className="h-4 w-4 mr-2" />
                View My Bookings
              </Button>
              <Button 
                onClick={() => navigate('/')} 
                variant="outline" 
                className="w-full"
              >
                <Home className="h-4 w-4 mr-2" />
                Return to Home
              </Button>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Need help? Contact our support team at{' '}
                <a href="mailto:support@skylyt.com" className="text-blue-600 hover:underline">
                  support@skylyt.com
                </a>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaymentConfirmation;