import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Car, 
  Hotel, 
  Calendar, 
  Users, 
  MapPin, 
  CreditCard, 
  Star,
  ArrowLeft,
  Check,
  Clock
} from 'lucide-react';
import Navigation from '@/components/Navigation';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';

const Booking = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user, isAuthenticated } = useAuth();
  
  const type = searchParams.get('type') || 'car';
  const itemId = searchParams.get('id') || '1';
  
  const [step, setStep] = useState(1);
  const [currentItem, setCurrentItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingData, setBookingData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    pickupDate: '',
    returnDate: '',
    pickupLocation: '',
    dropoffLocation: '',
    specialRequests: '',
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardName: '',
    bookingId: null
  });
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');

  useEffect(() => {
    if (user && isAuthenticated) {
      setBookingData(prev => ({
        ...prev,
        firstName: user.first_name || '',
        lastName: user.last_name || '',
        email: user.email || ''
      }));
    }
  }, [user, isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      const pendingBooking = localStorage.getItem('pendingBooking');
      if (pendingBooking) {
        const { bookingData: savedData } = JSON.parse(pendingBooking);
        setBookingData(prev => ({ ...prev, ...savedData }));
        localStorage.removeItem('pendingBooking');
        setStep(3);
      }
    }
  }, [isAuthenticated]);

  useEffect(() => {
    const fetchItemDetails = async () => {
      try {
        setLoading(true);
        const data = await apiService.request(`/bookings/summary/${type}/${itemId}`);
        setCurrentItem(data);
        
        if (type === 'hotel' && data.location) {
          setBookingData(prev => ({
            ...prev,
            pickupLocation: data.location
          }));
        }
      } catch (error) {
        console.error('Failed to fetch item details:', error);
        toast({
          title: "Error",
          description: "Failed to load item details",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };

    if (itemId) {
      fetchItemDetails();
    }
  }, [itemId, type, toast]);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!currentItem) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Item Not Found</h1>
            <p className="text-gray-600 mb-4">The {type} you're looking for doesn't exist.</p>
            <Button onClick={() => navigate(-1)}>Go Back</Button>
          </div>
        </div>
      </div>
    );
  }

  const hasBothDates = bookingData.pickupDate && bookingData.returnDate;
  
  const calculateDays = () => {
    if (!hasBothDates) return null;
    const pickup = new Date(bookingData.pickupDate);
    const returnDate = new Date(bookingData.returnDate);
    const diffTime = returnDate.getTime() - pickup.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(diffDays, 1);
  };

  const days = calculateDays();
  const basePrice = currentItem?.price || 0;
  const subtotal = hasBothDates && days ? basePrice * days : basePrice;
  const taxRate = 0.12;
  const taxes = hasBothDates && days ? Math.round(subtotal * taxRate) : 0;
  const finalTotal = subtotal + taxes;

  const handleInputChange = (field, value) => {
    setBookingData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      if (!isAuthenticated) {
        localStorage.setItem('pendingBooking', JSON.stringify({
          type,
          itemId,
          bookingData,
          finalTotal
        }));
        navigate(`/login?returnTo=${encodeURIComponent(window.location.pathname + window.location.search)}`);
        return;
      }

      try {
        const bookingPayload = {
          booking_type: type,
          booking_data: {
            item_id: itemId,
            guest_name: `${bookingData.firstName} ${bookingData.lastName}`,
            guest_email: bookingData.email,
            special_requests: bookingData.specialRequests,
            pickup_location: bookingData.pickupLocation,
            dropoff_location: bookingData.dropoffLocation
          },
          start_date: new Date(bookingData.pickupDate).toISOString(),
          end_date: new Date(bookingData.returnDate).toISOString(),
          total_amount: finalTotal,
          currency: 'USD'
        };

        const booking = await apiService.request('/bookings', {
          method: 'POST',
          body: JSON.stringify(bookingPayload)
        });
        
        setBookingData(prev => ({ ...prev, bookingId: booking.id }));
        setStep(4);
      } catch (error) {
        console.error('Booking creation error:', error);
        toast({
          title: "Booking Failed",
          description: "Unable to create booking. Please try again.",
          variant: "destructive",
        });
      }
    }
  };

  const handlePaymentMethodSelect = async (method) => {
    try {
      const bookingPayload = {
        booking_type: type,
        booking_data: {
          item_id: itemId,
          guest_name: `${bookingData.firstName} ${bookingData.lastName}`,
          guest_email: bookingData.email,
          special_requests: bookingData.specialRequests,
          pickup_location: bookingData.pickupLocation,
          dropoff_location: bookingData.dropoffLocation
        },
        start_date: new Date(bookingData.pickupDate).toISOString(),
        end_date: new Date(bookingData.returnDate).toISOString(),
        total_amount: finalTotal,
        currency: 'USD'
      };

      const booking = await apiService.request('/bookings', {
        method: 'POST',
        body: JSON.stringify(bookingPayload)
      });
      
      window.location.href = `/payment?bookingId=${booking.id}&amount=${finalTotal}&method=${method}`;
    } catch (error) {
      console.error('Booking creation error:', error);
      toast({
        title: "Booking Failed",
        description: "Unable to create booking. Please try again.",
        variant: "destructive",
      });
    }
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return bookingData.firstName && bookingData.lastName && bookingData.email;
      case 2:
        return bookingData.pickupDate && bookingData.returnDate && bookingData.pickupLocation;
      case 3:
        return true;
      case 4:
        return bookingData.bookingId;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center mb-6">
          <Button 
            variant="ghost" 
            onClick={() => navigate(-1)}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold">
            {type === 'car' ? 'Rent Your Car' : 'Book Your Hotel'}
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="flex items-center mb-8">
              {[1, 2, 3].map((stepNum) => (
                <div key={stepNum} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= stepNum ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step > stepNum ? <Check className="h-4 w-4" /> : stepNum}
                  </div>
                  <span className={`ml-2 text-sm ${step >= stepNum ? 'text-blue-600' : 'text-gray-500'}`}>
                    {stepNum === 1 ? 'Personal Info' : stepNum === 2 ? 'Booking Details' : 'Review & Confirm'}
                  </span>
                  {stepNum < 3 && <div className="w-8 h-px bg-gray-300 mx-4" />}
                </div>
              ))}
            </div>

            {step === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Personal Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">First Name</Label>
                      <Input
                        id="firstName"
                        value={bookingData.firstName}
                        onChange={(e) => handleInputChange('firstName', e.target.value)}
                        placeholder="Enter your first name"
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Last Name</Label>
                      <Input
                        id="lastName"
                        value={bookingData.lastName}
                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                        placeholder="Enter your last name"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={bookingData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="Enter your email"
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Booking Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="pickupDate">
                        {type === 'car' ? 'Pickup Date' : 'Check-in Date'}
                      </Label>
                      <Input
                        id="pickupDate"
                        type="date"
                        value={bookingData.pickupDate}
                        onChange={(e) => handleInputChange('pickupDate', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="returnDate">
                        {type === 'car' ? 'Return Date' : 'Check-out Date'}
                      </Label>
                      <Input
                        id="returnDate"
                        type="date"
                        value={bookingData.returnDate}
                        onChange={(e) => handleInputChange('returnDate', e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="pickupLocation">
                      {type === 'car' ? 'Pickup Location' : 'Hotel Location'}
                    </Label>
                    <Input
                      id="pickupLocation"
                      value={bookingData.pickupLocation}
                      onChange={(e) => handleInputChange('pickupLocation', e.target.value)}
                      placeholder={type === 'car' ? 'Enter pickup location' : 'Hotel location'}
                      readOnly={type === 'hotel'}
                      className={type === 'hotel' ? 'bg-gray-100 cursor-not-allowed' : ''}
                    />
                  </div>
                  {type === 'car' && (
                    <div>
                      <Label htmlFor="dropoffLocation">
                        Dropoff Location (Optional)
                      </Label>
                      <Input
                        id="dropoffLocation"
                        value={bookingData.dropoffLocation}
                        onChange={(e) => handleInputChange('dropoffLocation', e.target.value)}
                        placeholder="Enter dropoff location"
                      />
                    </div>
                  )}
                  <div>
                    <Label htmlFor="specialRequests">Special Requests (Optional)</Label>
                    <Textarea
                      id="specialRequests"
                      value={bookingData.specialRequests}
                      onChange={(e) => handleInputChange('specialRequests', e.target.value)}
                      placeholder="Any special requirements or preferences..."
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 3 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Check className="h-5 w-5" />
                    Review & Confirm
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">Booking Details</h4>
                    <div className="space-y-2 text-sm">
                      <p><strong>Name:</strong> {bookingData.firstName} {bookingData.lastName}</p>
                      <p><strong>Email:</strong> {bookingData.email}</p>
                      <p><strong>{type === 'car' ? 'Pickup' : 'Check-in'}:</strong> {bookingData.pickupDate}</p>
                      <p><strong>{type === 'car' ? 'Return' : 'Check-out'}:</strong> {bookingData.returnDate}</p>
                      <p><strong>Location:</strong> {bookingData.pickupLocation}</p>
                      {bookingData.specialRequests && (
                        <p><strong>Special Requests:</strong> {bookingData.specialRequests}</p>
                      )}
                    </div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-700">
                      By proceeding, you agree to our terms and conditions. You will be redirected to payment after confirmation.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 4 && (
              <>
                <div className="grid gap-4">
                  <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center gap-3">
                      <input 
                        type="radio" 
                        name="paymentMethod" 
                        className="w-4 h-4" 
                        checked={selectedPaymentMethod === 'stripe'}
                        onChange={() => setSelectedPaymentMethod('stripe')}
                      />
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <CreditCard className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold">Stripe</h3>
                        <p className="text-sm text-gray-600">Pay securely with credit/debit card</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center gap-3">
                      <input 
                        type="radio" 
                        name="paymentMethod" 
                        className="w-4 h-4" 
                        checked={selectedPaymentMethod === 'flutterwave'}
                        onChange={() => setSelectedPaymentMethod('flutterwave')}
                      />
                      <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                        <div className="w-6 h-6 bg-orange-600 rounded text-white text-xs flex items-center justify-center font-bold">
                          F
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold">Flutterwave</h3>
                        <p className="text-sm text-gray-600">Pay with Flutterwave gateway</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center gap-3">
                      <input 
                        type="radio" 
                        name="paymentMethod" 
                        className="w-4 h-4" 
                        checked={selectedPaymentMethod === 'paystack'}
                        onChange={() => setSelectedPaymentMethod('paystack')}
                      />
                      <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
                        <div className="w-6 h-6 bg-teal-600 rounded text-white text-xs flex items-center justify-center font-bold">
                          P
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold">Paystack</h3>
                        <p className="text-sm text-gray-600">Pay with Paystack gateway</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center gap-3">
                      <input 
                        type="radio" 
                        name="paymentMethod" 
                        className="w-4 h-4" 
                        checked={selectedPaymentMethod === 'paypal'}
                        onChange={() => setSelectedPaymentMethod('paypal')}
                      />
                      <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <div className="w-6 h-6 bg-yellow-600 rounded text-white text-xs flex items-center justify-center font-bold">
                          P
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold">PayPal</h3>
                        <p className="text-sm text-gray-600">Pay with your PayPal account</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center gap-3">
                      <input 
                        type="radio" 
                        name="paymentMethod" 
                        className="w-4 h-4" 
                        checked={selectedPaymentMethod === 'bank_transfer'}
                        onChange={() => setSelectedPaymentMethod('bank_transfer')}
                      />
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <div className="w-6 h-6 bg-green-600 rounded text-white text-xs flex items-center justify-center font-bold">
                          B
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold">Bank Transfer</h3>
                        <p className="text-sm text-gray-600">Direct bank transfer</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                {selectedPaymentMethod && (
                  <div className="mt-6">
                    <Button 
                      onClick={() => handlePaymentMethodSelect(selectedPaymentMethod)}
                      className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      Continue to Payment
                    </Button>
                  </div>
                )}
              </>
            )}

            {step < 4 && (
              <div className="flex justify-between mt-6">
                <Button 
                  variant="outline" 
                  onClick={() => setStep(Math.max(1, step - 1))}
                  disabled={step === 1}
                >
                  Previous
                </Button>
                <Button 
                  onClick={handleSubmit}
                  disabled={!isStepValid()}
                  className="bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  {step === 3 ? 'Proceed to Payment' : 'Next Step'}
                </Button>
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Booking Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-4">
                  <img
                    src={currentItem.image_url || '/placeholder.svg'}
                    alt={currentItem.name}
                    className="w-16 h-16 rounded-lg object-cover"
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold">{currentItem.name}</h3>
                    <div className="flex items-center mt-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600 ml-1">{currentItem.rating || 4.5}</span>
                    </div>
                    {type === 'car' && (
                      <div className="flex items-center text-sm text-gray-600 mt-1">
                        <Users className="h-3 w-3 mr-1" />
                        {currentItem.passengers} seats
                      </div>
                    )}
                    {type === 'hotel' && (
                      <div className="flex items-center text-sm text-gray-600 mt-1">
                        <MapPin className="h-3 w-3 mr-1" />
                        {currentItem.location}
                      </div>
                    )}
                  </div>
                </div>

                <Separator />

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>{type === 'car' ? 'Daily Rate' : 'Nightly Rate'}</span>
                    <span>${basePrice.toLocaleString()}</span>
                  </div>
                  {hasBothDates && days && (
                    <>
                      <div className="flex justify-between">
                        <span>Duration</span>
                        <span>{days} {days === 1 ? 'day' : 'days'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Subtotal</span>
                        <span>${subtotal.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Taxes & Fees (12%)</span>
                        <span>${taxes.toLocaleString()}</span>
                      </div>
                    </>
                  )}
                  {!hasBothDates && (
                    <div className="text-gray-500 text-xs italic">
                      Select dates to calculate total price
                    </div>
                  )}
                </div>

                <Separator />

                <div className="flex justify-between font-semibold text-lg">
                  <span>{hasBothDates ? 'Total' : 'Base Price'}</span>
                  <span className="text-blue-600">${finalTotal.toLocaleString()}</span>
                </div>

                <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                  <div className="flex items-center text-green-700 text-sm">
                    <Check className="h-4 w-4 mr-2" />
                    Free cancellation up to 24 hours before {type === 'car' ? 'pickup' : 'check-in'}
                  </div>
                </div>

                <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                  <div className="flex items-center text-blue-700 text-sm">
                    <Clock className="h-4 w-4 mr-2" />
                    Instant confirmation
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Booking;