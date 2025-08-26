import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Hotel, Edit, Trash2 } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

const HotelBookingManagement = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingBooking, setEditingBooking] = useState(null);
  const [editForm, setEditForm] = useState({ status: '' });
  const { hasPermission } = useAuth();

  useEffect(() => {
    fetchHotelBookings();
  }, []);

  const fetchHotelBookings = async () => {
    try {
      const data = await apiService.request('/admin/hotel-bookings');
      setBookings(data.bookings || []);
    } catch (error) {
      console.error('Failed to fetch hotel bookings:', error);
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

  const handleSaveBooking = async () => {
    if (!editingBooking) return;
    
    try {
      await apiService.updateBookingStatus(editingBooking.id, editForm.status);
      fetchHotelBookings();
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Failed to update booking:', error);
    }
  };

  const handleDeleteBooking = async (bookingId) => {
    if (!confirm('Are you sure you want to delete this hotel booking?')) return;
    
    try {
      await apiService.request(`/admin/bookings/${bookingId}`, { method: 'DELETE' });
      fetchHotelBookings();
    } catch (error) {
      console.error('Failed to delete booking:', error);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hotel className="h-5 w-5" />
            Hotel Bookings
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
        <CardTitle className="flex items-center gap-2">
          <Hotel className="h-5 w-5" />
          Hotel Bookings ({bookings.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {bookings.length === 0 ? (
          <div className="text-center py-8">
            <Hotel className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No hotel bookings found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((booking) => (
              <div key={booking.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <Hotel className="h-5 w-5 text-blue-600 mt-1" />
                    <div>
                      <h3 className="font-semibold">#{booking.booking_reference}</h3>
                      <p className="text-sm text-gray-600">{booking.hotel_name}</p>
                      <p className="text-sm text-gray-600">
                        ${booking.total_amount} {booking.currency}
                      </p>
                      <p className="text-sm text-gray-600">
                        Guest: {booking.customer_name}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(booking.status)}>
                      {booking.status}
                    </Badge>
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
      
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Hotel Booking #{editingBooking?.booking_reference}</DialogTitle>
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
    </Card>
  );
};

export default HotelBookingManagement;