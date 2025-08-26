import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  Users, 
  Star, 
  Car,
  Hotel,
  CreditCard,
  Phone,
  Mail
} from 'lucide-react';
import Navigation from '@/components/Navigation';

const BookingDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Sample booking data - in real app this would come from API
  const booking = {
    id: id || '1',
    type: 'car',
    item: 'BMW 3 Series',
    image: '/placeholder.svg',
    status: 'Confirmed',
    startDate: '2024-01-15',
    endDate: '2024-01-18',
    location: 'New York, NY',
    amount: 267,
    bookingRef: 'BK' + (id || '1').padStart(6, '0'),
    customerName: 'John Doe',
    customerEmail: 'john.doe@example.com',
    customerPhone: '+1 (555) 123-4567'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center mb-6">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/dashboard')}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold">Booking Details</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Details */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    {booking.type === 'car' ? <Car className="h-5 w-5" /> : <Hotel className="h-5 w-5" />}
                    {booking.item}
                  </CardTitle>
                  <Badge variant={booking.status === 'Confirmed' ? 'default' : 'secondary'}>
                    {booking.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-start space-x-4 mb-6">
                  <img
                    src={booking.image}
                    alt={booking.item}
                    className="w-24 h-24 rounded-lg object-cover"
                  />
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2">{booking.item}</h3>
                    <div className="flex items-center text-gray-600 mb-2">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span>{booking.location}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Star className="h-4 w-4 text-yellow-400 fill-current mr-1" />
                      <span>4.8 rating</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-2">Booking Information</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Booking Reference:</span>
                        <span className="font-medium">{booking.bookingRef}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">
                          {booking.type === 'car' ? 'Pickup Date:' : 'Check-in:'}
                        </span>
                        <span className="font-medium">{booking.startDate}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">
                          {booking.type === 'car' ? 'Return Date:' : 'Check-out:'}
                        </span>
                        <span className="font-medium">{booking.endDate}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Amount:</span>
                        <span className="font-medium text-green-600">${booking.amount}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Customer Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{booking.customerName}</span>
                      </div>
                      <div className="flex items-center">
                        <Mail className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{booking.customerEmail}</span>
                      </div>
                      <div className="flex items-center">
                        <Phone className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{booking.customerPhone}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Payment Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center">
                    <CreditCard className="h-5 w-5 text-green-600 mr-3" />
                    <div>
                      <p className="font-medium text-green-800">Payment Confirmed</p>
                      <p className="text-sm text-green-600">Paid via Visa •••• 4242</p>
                    </div>
                  </div>
                  <span className="font-bold text-green-600">${booking.amount}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Actions Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full" variant="outline">
                  Download Receipt
                </Button>
                <Button className="w-full" variant="outline">
                  Contact Support
                </Button>
                <Button className="w-full" variant="outline">
                  Modify Booking
                </Button>
                <Button variant="outline" className="w-full text-red-600 border-red-200 hover:bg-red-50">
                  Cancel Booking
                </Button>
              </CardContent>
            </Card>

            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Important Information</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p className="text-gray-600">
                  • Free cancellation up to 24 hours before pickup
                </p>
                <p className="text-gray-600">
                  • Bring a valid driver's license and credit card
                </p>
                <p className="text-gray-600">
                  • Fuel tank should be returned at the same level
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingDetails;