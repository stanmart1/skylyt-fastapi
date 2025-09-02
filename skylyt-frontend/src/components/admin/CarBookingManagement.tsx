import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Car, Edit, Trash2, Eye, User, Calendar, MapPin, CreditCard, Phone, Mail, Plus } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import PriceDisplay from '@/components/PriceDisplay';
import { useCurrency } from '@/contexts/CurrencyContext';
import AddCarBookingModal from './AddCarBookingModal';

const CarBookingManagement = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingBooking, setEditingBooking] = useState(null);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [bookingDetails, setBookingDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [editForm, setEditForm] = useState({ status: '' });
  const { hasPermission } = useAuth();
  const { currency } = useCurrency();

  useEffect(() => {
    fetchCarBookings();
  }, []);

  const fetchCarBookings = async () => {
    try {
      const data = await apiService.request('/admin/car-bookings');
      setBookings(data.bookings || []);
    } catch (error) {
      console.error('Failed to fetch car bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleEditBooking = (booking) => {
    setEditingBooking(booking);
    setEditForm({ status: booking.status });
    setIsEditModalOpen(true);
  };

  const handleViewDetails = async (booking) => {
    setSelectedBooking(booking);
    setIsDetailsModalOpen(true);
    setDetailsLoading(true);
    
    try {
      const details = await apiService.request(`/admin/bookings/${booking.id}/details`);
      setBookingDetails(details);
    } catch (error) {
      console.error('Failed to fetch booking details:', error);
      // Fallback to basic booking data if detailed endpoint fails
      setBookingDetails(booking);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleSaveBooking = async () => {
    if (!editingBooking) return;
    
    try {
      await apiService.updateBookingStatus(editingBooking.id, editForm.status);
      fetchCarBookings();
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Failed to update booking:', error);
    }
  };

  const handleDeleteBooking = async (bookingId) => {
    if (!confirm('Are you sure you want to delete this car booking?')) return;
    
    try {
      await apiService.request(`/admin/bookings/${bookingId}`, { method: 'DELETE' });
      fetchCarBookings();
    } catch (error) {
      console.error('Failed to delete booking:', error);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Car className="h-5 w-5" />
            Car Rentals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Car className="h-5 w-5" />
            Car Rentals ({bookings.length})
          </CardTitle>
          {hasPermission('bookings.create') && (
            <Button onClick={() => setIsAddModalOpen(true)} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add Car Booking
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {bookings.length === 0 ? (
          <div className="text-center py-8">
            <Car className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No car bookings found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((booking) => (
              <div key={booking.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <Car className="h-5 w-5 text-green-600 mt-1" />
                    <div>
                      <h3 className="font-semibold">#{booking.booking_reference}</h3>
                      <p className="text-sm text-gray-600">{booking.car_name}</p>
                      <p className="text-sm text-gray-600">
                        ${booking.total_amount} {booking.currency}
                      </p>
                      <p className="text-sm text-gray-600">
                        Renter: {booking.customer_name}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(booking.status)}>
                      {booking.status}
                    </Badge>
                    <Button variant="outline" size="sm" onClick={() => handleViewDetails(booking)}>
                      <Eye className="h-3 w-3" />
                    </Button>
                    {hasPermission('bookings.update') && (
                      <Button variant="outline" size="sm" onClick={() => handleEditBooking(booking)}>
                        <Edit className="h-3 w-3" />
                      </Button>
                    )}
                    {hasPermission('bookings.delete') && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDeleteBooking(booking.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      
      {/* Edit Booking Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Car Booking #{editingBooking?.booking_reference}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Status</label>
              <Select value={editForm.status} onValueChange={(value) => setEditForm({status: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSaveBooking}>Save</Button>
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Booking Details Modal */}
      <Dialog open={isDetailsModalOpen} onOpenChange={setIsDetailsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Car className="h-5 w-5" />
              Booking Details #{selectedBooking?.booking_reference}
            </DialogTitle>
            <DialogDescription>
              Complete information for this car rental booking
            </DialogDescription>
          </DialogHeader>
          
          {detailsLoading ? (
            <div className="space-y-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
              ))}
            </div>
          ) : bookingDetails ? (
            <div className="space-y-6">
              {/* Booking Status */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    bookingDetails.status === 'confirmed' ? 'bg-green-500' :
                    bookingDetails.status === 'pending' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className="font-medium">Status: {bookingDetails.status}</span>
                </div>
                <Badge className={getStatusColor(bookingDetails.status)}>
                  {bookingDetails.status}
                </Badge>
              </div>

              {/* Customer Information */}
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Customer Information
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 border rounded-lg">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Name</label>
                    <p className="font-medium">{bookingDetails.customer_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Email</label>
                    <p className="font-medium flex items-center gap-1">
                      <Mail className="h-3 w-3" />
                      {bookingDetails.customer_email || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Phone</label>
                    <p className="font-medium flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      {bookingDetails.customer_phone || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">User ID</label>
                    <p className="font-medium">{bookingDetails.user_id || 'N/A'}</p>
                  </div>
                </div>
              </div>

              {/* Car Information */}
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Car className="h-4 w-4" />
                  Vehicle Information
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 border rounded-lg">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Car Name</label>
                    <p className="font-medium">{bookingDetails.car_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Car ID</label>
                    <p className="font-medium">{bookingDetails.car_id || 'N/A'}</p>
                  </div>
                </div>
              </div>

              {/* Booking Dates */}
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Rental Period
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 border rounded-lg">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Start Date</label>
                    <p className="font-medium">
                      {bookingDetails.start_date ? new Date(bookingDetails.start_date).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">End Date</label>
                    <p className="font-medium">
                      {bookingDetails.end_date ? new Date(bookingDetails.end_date).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Duration</label>
                    <p className="font-medium">
                      {bookingDetails.start_date && bookingDetails.end_date ? 
                        Math.ceil((new Date(bookingDetails.end_date) - new Date(bookingDetails.start_date)) / (1000 * 60 * 60 * 24)) + ' days'
                        : 'N/A'
                      }
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Booking Date</label>
                    <p className="font-medium">
                      {bookingDetails.created_at ? new Date(bookingDetails.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Payment Information */}
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <CreditCard className="h-4 w-4" />
                  Payment Information
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 border rounded-lg">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Total Amount</label>
                    <p className="font-medium text-lg">
                      <PriceDisplay amount={bookingDetails.total_amount || 0} currency={bookingDetails.currency || currency} />
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Payment Status</label>
                    <p className="font-medium">{bookingDetails.payment_status || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Currency</label>
                    <p className="font-medium">{bookingDetails.currency || currency}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Confirmation Number</label>
                    <p className="font-medium">{bookingDetails.confirmation_number || 'N/A'}</p>
                  </div>
                </div>
              </div>

              {/* Additional Information */}
              {(bookingDetails.special_requests || bookingDetails.booking_data) && (
                <div className="space-y-3">
                  <h3 className="font-semibold flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Additional Information
                  </h3>
                  <div className="p-4 border rounded-lg space-y-3">
                    {bookingDetails.special_requests && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">Special Requests</label>
                        <p className="font-medium">{bookingDetails.special_requests}</p>
                      </div>
                    )}
                    {bookingDetails.external_booking_id && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">External Booking ID</label>
                        <p className="font-medium">{bookingDetails.external_booking_id}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">Failed to load booking details</p>
            </div>
          )}
          
          <div className="flex justify-end pt-4">
            <Button variant="outline" onClick={() => setIsDetailsModalOpen(false)}>Close</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Car Booking Modal */}
      <AddCarBookingModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={fetchCarBookings}
      />
    </Card>
  );
};

export default CarBookingManagement;