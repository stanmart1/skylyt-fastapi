import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Calendar, Car, Hotel, User, Edit, Trash2, Trash } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { Booking } from '@/types/api';
import PriceDisplay from '@/components/PriceDisplay';

const BookingManagement = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingBooking, setEditingBooking] = useState<Booking | null>(null);
  const [editForm, setEditForm] = useState({
    status: '',
    driver_id: ''
  });
  const [drivers, setDrivers] = useState<any[]>([]);
  const [selectedBookings, setSelectedBookings] = useState<number[]>([]);
  const { hasPermission } = useAuth();

  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const data = await apiService.getAllBookings();
        setBookings(data);
      } catch (error) {
        console.error('Failed to fetch bookings:', error);
      } finally {
        setLoading(false);
      }
    };

    const fetchDrivers = async () => {
      try {
        const data = await apiService.request('/drivers?is_active=true');
        setDrivers(data || []);
      } catch (error) {
        console.error('Failed to fetch drivers:', error);
      }
    };

    fetchBookings();
    fetchDrivers();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getBookingIcon = (type: string) => {
    return type === 'hotel' ? Hotel : Car;
  };

  const handleEditBooking = (booking: Booking) => {
    setEditingBooking(booking);
    setEditForm({
      status: booking.status,
      driver_id: (booking as any).driver_id || ''
    });
    setIsEditModalOpen(true);
  };

  const handleSaveBooking = async () => {
    if (!editingBooking) return;
    
    try {
      await apiService.request(`/admin/bookings/${editingBooking.id}`, {
        method: 'PUT',
        body: JSON.stringify(editForm)
      });
      
      // Refresh bookings
      const data = await apiService.getAllBookings();
      setBookings(data);
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Failed to update booking:', error);
    }
  };

  const handleDeleteBooking = async (bookingId: number) => {
    try {
      await apiService.request(`/admin/bookings/${bookingId}`, {
        method: 'DELETE'
      });
      
      // Refresh bookings
      const data = await apiService.getAllBookings();
      setBookings(data);
    } catch (error) {
      console.error('Failed to delete booking:', error);
    }
  };

  const handleRefundBooking = async (bookingId: number) => {
    try {
      await apiService.request(`/admin/bookings/${bookingId}/refund`, {
        method: 'POST'
      });
      
      // Refresh bookings
      const data = await apiService.getAllBookings();
      setBookings(data);
    } catch (error) {
      console.error('Failed to process refund:', error);
    }
  };

  const handleTrackSource = async (bookingId: number) => {
    try {
      const sourceData = await apiService.request(`/admin/bookings/${bookingId}/source`);
      // Display source tracking information
      alert(`Booking Source: ${sourceData.source || 'Direct'} | Referrer: ${sourceData.referrer || 'None'}`);
    } catch (error) {
      console.error('Failed to fetch booking source:', error);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedBookings.length === 0) return;
    if (!confirm(`Are you sure you want to delete ${selectedBookings.length} bookings?`)) return;
    
    try {
      await apiService.request('/admin/bookings/bulk', {
        method: 'DELETE',
        body: JSON.stringify({ ids: selectedBookings })
      });
      
      // Refresh bookings and clear selection
      const data = await apiService.getAllBookings();
      setBookings(data);
      setSelectedBookings([]);
    } catch (error) {
      console.error('Failed to bulk delete bookings:', error);
    }
  };

  const handleSelectBooking = (bookingId: number) => {
    setSelectedBookings(prev => 
      prev.includes(bookingId) 
        ? prev.filter(id => id !== bookingId)
        : [...prev, bookingId]
    );
  };

  const handleSelectAll = () => {
    if (selectedBookings.length === bookings.length) {
      setSelectedBookings([]);
    } else {
      setSelectedBookings(bookings.map(b => b.id));
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Booking Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
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
            <Calendar className="h-5 w-5" />
            Booking Management
          </CardTitle>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={selectedBookings.length === bookings.length && bookings.length > 0}
              onChange={handleSelectAll}
              className="w-4 h-4"
            />
            <button
              onClick={handleSelectAll}
              className="px-3 py-1 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-teal-600 rounded hover:from-blue-700 hover:to-teal-700 transition-colors"
            >
              Select All ({selectedBookings.length} selected)
            </button>
            {selectedBookings.length > 0 && (
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={handleBulkDelete}
                className="flex items-center gap-2 ml-2"
              >
                <Trash className="h-4 w-4" />
                Delete Selected ({selectedBookings.length})
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {bookings.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No bookings found</p>
          </div>
        ) : (
          <div className="space-y-4">

            {bookings.map((booking) => {
              const Icon = getBookingIcon(booking.booking_type);
              const isSelected = selectedBookings.includes(booking.id);
              return (
                <div key={booking.id} className={`border rounded-lg p-4 ${isSelected ? 'bg-blue-50 border-blue-200' : ''}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleSelectBooking(booking.id)}
                        className="w-4 h-4 mt-1"
                      />
                      <Icon className="h-5 w-5 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold">
                          Booking #{booking.id}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Type: {booking.booking_type}
                        </p>
                        {(booking as any).driver_name && (
                          <p className="text-sm text-gray-600">
                            Driver: {(booking as any).driver_name}
                          </p>
                        )}
                        <p className="text-sm text-gray-600">
                          Amount: <PriceDisplay 
                            amount={booking.total_amount} 
                            currency={booking.currency}
                            isNGNStored={true}
                          />
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
              );
            })}
          </div>
        )}
      </CardContent>
      
      {/* Edit Booking Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Booking Details #{editingBooking?.id}</DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            {/* Booking Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-600">Booking Reference</Label>
                <p className="text-sm">{editingBooking?.booking_reference}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Booking Type</Label>
                <p className="text-sm capitalize">{editingBooking?.booking_type}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Check-in Date</Label>
                <p className="text-sm">{editingBooking?.check_in_date ? new Date(editingBooking.check_in_date).toLocaleDateString() : 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Check-out Date</Label>
                <p className="text-sm">{editingBooking?.check_out_date ? new Date(editingBooking.check_out_date).toLocaleDateString() : 'N/A'}</p>
              </div>
            </div>

            {/* Item Details */}
            <div>
              <Label className="text-sm font-medium text-gray-600">Item Details</Label>
              <div className="bg-gray-50 p-3 rounded-lg mt-1">
                <p className="font-medium">{editingBooking?.hotel_name || editingBooking?.car_name || 'N/A'}</p>
                {editingBooking?.booking_data && (
                  <div className="text-sm text-gray-600 mt-1">
                    <p>Pickup Location: {JSON.parse(editingBooking.booking_data).pickup_location || 'N/A'}</p>
                    {JSON.parse(editingBooking.booking_data).dropoff_location && (
                      <p>Dropoff Location: {JSON.parse(editingBooking.booking_data).dropoff_location}</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Customer Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-600">Customer Name</Label>
                <p className="text-sm">{editingBooking?.customer_name || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Customer Email</Label>
                <p className="text-sm">{editingBooking?.customer_email || 'N/A'}</p>
              </div>
            </div>

            {/* Booking Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="status">Status</Label>
                <Select value={editForm.status} onValueChange={(value) => setEditForm({...editForm, status: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="confirmed">Confirmed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">Total Amount</Label>
                <p className="text-sm font-bold">
                  <PriceDisplay 
                    amount={editingBooking?.total_amount || 0} 
                    currency={editingBooking?.currency}
                    isNGNStored={true}
                  />
                </p>
              </div>
            </div>

            {/* Driver Assignment (for car bookings) */}
            {editingBooking?.booking_type === 'car' && (
              <div>
                <Label htmlFor="driver">Assign Driver</Label>
                <Select value={editForm.driver_id} onValueChange={(value) => setEditForm({...editForm, driver_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select driver (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No driver assigned</SelectItem>
                    {drivers.filter(d => d.is_available).map((driver) => (
                      <SelectItem key={driver.id} value={driver.id.toString()}>
                        {driver.name} - {driver.license_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label className="text-sm font-medium text-gray-600">Special Requests</Label>
              <p className="text-sm">{editingBooking?.special_requests || 'None'}</p>
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveBooking}>
                Save Changes
              </Button>
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export { BookingManagement };