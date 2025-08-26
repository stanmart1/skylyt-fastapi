import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ConfirmationDialog } from '@/components/ui/confirmation-dialog';
import { useToast } from '@/components/ui/toast';
import { Calendar, Car, Hotel, User, Edit, Trash2, Trash, Search, Filter, Download, Mail, X, ChevronLeft, ChevronRight, MoreVertical } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { useBooking } from '@/contexts/BookingContext';
import { Booking } from '@/types/api';

const EnhancedBookingManagement = () => {
  const { state, actions } = useBooking();
  const { addToast } = useToast();
  const { hasPermission } = useAuth();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ status: '' });
  const [selectedBookings, setSelectedBookings] = useState<number[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    message: string;
    action: () => void;
    variant?: 'default' | 'destructive';
  }>({ open: false, title: '', message: '', action: () => {} });
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchBookings();
  }, [state.filters, state.pagination.page]);

  const fetchBookings = async () => {
    try {
      actions.setLoading(true);
      const params = {
        ...state.filters,
        page: state.pagination.page,
        perPage: state.pagination.perPage
      };
      
      // Remove empty values
      Object.keys(params).forEach(key => {
        if (params[key as keyof typeof params] === '') {
          delete params[key as keyof typeof params];
        }
      });
      
      const data = await apiService.getAllBookings(params);
      actions.setBookings(data);
    } catch (error) {
      actions.setError('Failed to fetch bookings');
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch bookings'
      });
    }
  };

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
    actions.setSelectedBooking(booking);
    setEditForm({ status: booking.status });
    setIsEditModalOpen(true);
  };

  const handleViewDetails = async (booking: Booking) => {
    try {
      actions.setLoading(true);
      const details = await apiService.getBookingDetails(booking.id);
      actions.setSelectedBooking(details);
      setIsDetailModalOpen(true);
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to load booking details'
      });
    } finally {
      actions.setLoading(false);
    }
  };

  const handleSaveBooking = async () => {
    if (!state.selectedBooking) return;
    
    try {
      setActionLoading('save');
      await apiService.updateBookingStatus(state.selectedBooking.id, editForm.status);
      
      addToast({
        type: 'success',
        title: 'Success',
        message: 'Booking updated successfully'
      });
      
      setIsEditModalOpen(false);
      fetchBookings();
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to update booking'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteBooking = (bookingId: number) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Booking',
      message: 'Are you sure you want to delete this booking? This action cannot be undone.',
      variant: 'destructive',
      action: () => deleteBooking(bookingId)
    });
  };

  const deleteBooking = async (bookingId: number) => {
    try {
      setActionLoading('delete');
      await apiService.request(`/admin/bookings/${bookingId}`, {
        method: 'DELETE'
      });
      
      addToast({
        type: 'success',
        title: 'Success',
        message: 'Booking deleted successfully'
      });
      
      fetchBookings();
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to delete booking'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleBulkDelete = () => {
    if (selectedBookings.length === 0) return;
    
    setConfirmDialog({
      open: true,
      title: 'Delete Bookings',
      message: `Are you sure you want to delete ${selectedBookings.length} bookings? This action cannot be undone.`,
      variant: 'destructive',
      action: bulkDeleteBookings
    });
  };

  const bulkDeleteBookings = async () => {
    try {
      setActionLoading('bulk-delete');
      await apiService.request('/admin/bookings/bulk', {
        method: 'DELETE',
        body: JSON.stringify({ ids: selectedBookings })
      });
      
      addToast({
        type: 'success',
        title: 'Success',
        message: `${selectedBookings.length} bookings deleted successfully`
      });
      
      setSelectedBookings([]);
      fetchBookings();
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to delete bookings'
      });
    } finally {
      setActionLoading(null);
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
    if (selectedBookings.length === state.bookings.length) {
      setSelectedBookings([]);
    } else {
      setSelectedBookings(state.bookings.map(b => b.id));
    }
  };

  const handleResendConfirmation = async (bookingId: number) => {
    try {
      setActionLoading(`resend-${bookingId}`);
      await apiService.resendBookingConfirmation(bookingId);
      
      addToast({
        type: 'success',
        title: 'Success',
        message: 'Confirmation email sent successfully'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to send confirmation email'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownloadInvoice = async (bookingId: number) => {
    try {
      setActionLoading(`invoice-${bookingId}`);
      const invoiceData = await apiService.getBookingInvoice(bookingId);
      
      // Create and download invoice (simplified)
      const dataStr = JSON.stringify(invoiceData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice-${invoiceData.booking_reference}.json`;
      link.click();
      URL.revokeObjectURL(url);
      
      addToast({
        type: 'success',
        title: 'Success',
        message: 'Invoice downloaded successfully'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to download invoice'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancelBooking = (bookingId: number) => {
    setConfirmDialog({
      open: true,
      title: 'Cancel Booking',
      message: 'Are you sure you want to cancel this booking?',
      variant: 'destructive',
      action: () => cancelBooking(bookingId)
    });
  };

  const cancelBooking = async (bookingId: number) => {
    try {
      setActionLoading(`cancel-${bookingId}`);
      await apiService.cancelBookingAdmin(bookingId, 'Cancelled by admin');
      
      addToast({
        type: 'success',
        title: 'Success',
        message: 'Booking cancelled successfully'
      });
      
      fetchBookings();
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to cancel booking'
      });
    } finally {
      setActionLoading(null);
    }
  };

  if (state.loading) {
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
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Booking Management
          </CardTitle>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedBookings.length === state.bookings.length && state.bookings.length > 0}
                onChange={handleSelectAll}
                className="w-4 h-4"
              />
              <button
                onClick={handleSelectAll}
                className="px-3 py-1 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-teal-600 rounded hover:from-blue-700 hover:to-teal-700 transition-colors"
              >
                <span className="hidden sm:inline">Select All</span>
                <span className="sm:hidden">All</span> ({selectedBookings.length})
              </button>
            </div>
            {selectedBookings.length > 0 && (
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={handleBulkDelete}
                disabled={actionLoading === 'bulk-delete'}
                className="flex items-center gap-2"
              >
                <Trash className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {actionLoading === 'bulk-delete' ? 'Deleting...' : `Delete Selected (${selectedBookings.length})`}
                </span>
                <span className="sm:hidden">
                  {actionLoading === 'bulk-delete' ? 'Deleting...' : `Delete (${selectedBookings.length})`}
                </span>
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Search and Filters */}
        <div className="space-y-4 mb-6">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search bookings..."
                value={state.filters.search}
                onChange={(e) => actions.setFilters({ search: e.target.value })}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 flex-1 sm:flex-none"
              >
                <Filter className="h-4 w-4" />
                <span className="hidden sm:inline">Filters</span>
              </Button>
              <Button
                variant="outline"
                onClick={() => actions.resetFilters()}
                className="flex-1 sm:flex-none"
              >
                Clear
              </Button>
            </div>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
              <Select value={state.filters.status || 'all'} onValueChange={(value) => actions.setFilters({ status: value === 'all' ? '' : value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>

              <Select value={state.filters.paymentStatus || 'all'} onValueChange={(value) => actions.setFilters({ paymentStatus: value === 'all' ? '' : value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Payment Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Payment Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>

              <Select value={state.filters.bookingType || 'all'} onValueChange={(value) => actions.setFilters({ bookingType: value === 'all' ? '' : value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="hotel">Hotel</SelectItem>
                  <SelectItem value="car">Car</SelectItem>
                </SelectContent>
              </Select>

              <Select value={state.filters.sortBy} onValueChange={(value) => actions.setFilters({ sortBy: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Sort By" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="created_at">Created Date</SelectItem>
                  <SelectItem value="customer_name">Customer Name</SelectItem>
                  <SelectItem value="total_amount">Amount</SelectItem>
                  <SelectItem value="status">Status</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {state.bookings.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No bookings found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {state.bookings.map((booking) => {
              const Icon = getBookingIcon(booking.booking_type);
              const isSelected = selectedBookings.includes(booking.id);
              return (
                <div key={booking.id} className={`border rounded-lg p-4 ${isSelected ? 'bg-blue-50 border-blue-200' : ''}`}>
                  <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleSelectBooking(booking.id)}
                        className="w-4 h-4 mt-1 flex-shrink-0"
                      />
                      <Icon className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold cursor-pointer hover:text-blue-600 truncate" onClick={() => handleViewDetails(booking)}>
                          Booking #{booking.id}
                        </h3>
                        <p className="text-sm text-gray-600 truncate">
                          {booking.customer_name} • {booking.customer_email}
                        </p>
                        <p className="text-sm text-gray-600 truncate">
                          {booking.booking_type === 'hotel' ? booking.hotel_name : booking.car_name}
                        </p>
                        <p className="text-sm font-medium">
                          ${booking.total_amount} {booking.currency}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
                      <div className="flex flex-row sm:flex-col gap-2 sm:gap-1">
                        <Badge className={getStatusColor(booking.status)}>
                          {booking.status}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {booking.payment_status}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-1 overflow-x-auto">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleViewDetails(booking)}
                          title="View Details"
                          className="flex-shrink-0"
                        >
                          <User className="h-3 w-3" />
                        </Button>
                        
                        {hasPermission('bookings.update') && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleEditBooking(booking)}
                            title="Edit"
                            className="flex-shrink-0"
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                        )}
                        
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleResendConfirmation(booking.id)}
                          disabled={actionLoading === `resend-${booking.id}`}
                          title="Resend Confirmation"
                          className="flex-shrink-0"
                        >
                          <Mail className="h-3 w-3" />
                        </Button>
                        
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleDownloadInvoice(booking.id)}
                          disabled={actionLoading === `invoice-${booking.id}`}
                          title="Download Invoice"
                          className="flex-shrink-0"
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                        
                        {booking.status !== 'cancelled' && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleCancelBooking(booking.id)}
                            disabled={actionLoading === `cancel-${booking.id}`}
                            className="text-orange-600 hover:text-orange-700 flex-shrink-0"
                            title="Cancel Booking"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        )}
                        
                        {hasPermission('bookings.delete') && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-red-600 hover:text-red-700 flex-shrink-0"
                            onClick={() => handleDeleteBooking(booking.id)}
                            disabled={actionLoading === 'delete'}
                            title="Delete"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {state.pagination.totalPages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between mt-6 pt-4 border-t gap-4">
            <div className="text-sm text-gray-600 text-center sm:text-left">
              Showing {((state.pagination.page - 1) * state.pagination.perPage) + 1} to {Math.min(state.pagination.page * state.pagination.perPage, state.pagination.total)} of {state.pagination.total} bookings
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => actions.setPagination({ page: state.pagination.page - 1 })}
                disabled={state.pagination.page === 1}
                className="flex items-center gap-1"
              >
                <ChevronLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Previous</span>
              </Button>
              <span className="text-sm px-2">
                <span className="hidden sm:inline">Page </span>{state.pagination.page}<span className="hidden sm:inline"> of {state.pagination.totalPages}</span>
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => actions.setPagination({ page: state.pagination.page + 1 })}
                disabled={state.pagination.page === state.pagination.totalPages}
                className="flex items-center gap-1"
              >
                <span className="hidden sm:inline">Next</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
      
      {/* Edit Booking Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Booking #{state.selectedBooking?.id}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
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

            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveBooking} disabled={actionLoading === 'save'}>
                {actionLoading === 'save' ? 'Saving...' : 'Save Changes'}
              </Button>
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Booking Details Modal */}
      <Dialog open={isDetailModalOpen} onOpenChange={setIsDetailModalOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Booking Details #{state.selectedBooking?.id}</DialogTitle>
          </DialogHeader>
          {state.selectedBooking && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">Booking Reference</Label>
                  <p className="text-sm font-mono break-all">{state.selectedBooking.booking_reference}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Booking Type</Label>
                  <p className="text-sm capitalize">{state.selectedBooking.booking_type}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Status</Label>
                  <Badge className={getStatusColor(state.selectedBooking.status)}>
                    {state.selectedBooking.status}
                  </Badge>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Payment Status</Label>
                  <Badge variant="outline">{state.selectedBooking.payment_status}</Badge>
                </div>
              </div>

              {/* Customer Information */}
              <div>
                <h3 className="font-medium mb-2">Customer Information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Name</Label>
                    <p className="text-sm break-words">{state.selectedBooking.customer_name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Email</Label>
                    <p className="text-sm break-all">{state.selectedBooking.customer_email}</p>
                  </div>
                </div>
              </div>

              {/* Booking Details */}
              <div>
                <h3 className="font-medium mb-2">Booking Details</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Item</Label>
                    <p className="text-sm break-words">{state.selectedBooking.hotel_name || state.selectedBooking.car_name || 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Total Amount</Label>
                    <p className="text-sm font-bold">${state.selectedBooking.total_amount} {state.selectedBooking.currency}</p>
                  </div>
                  {state.selectedBooking.check_in_date && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Check-in Date</Label>
                      <p className="text-sm">{new Date(state.selectedBooking.check_in_date).toLocaleDateString()}</p>
                    </div>
                  )}
                  {state.selectedBooking.check_out_date && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Check-out Date</Label>
                      <p className="text-sm">{new Date(state.selectedBooking.check_out_date).toLocaleDateString()}</p>
                    </div>
                  )}
                  {state.selectedBooking.number_of_guests && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Guests</Label>
                      <p className="text-sm">{state.selectedBooking.number_of_guests}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Special Requests */}
              {state.selectedBooking.special_requests && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Special Requests</Label>
                  <p className="text-sm bg-gray-50 p-3 rounded break-words">{state.selectedBooking.special_requests}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-2 pt-4 border-t">
                <Button onClick={() => handleResendConfirmation(state.selectedBooking!.id)} disabled={actionLoading?.startsWith('resend')} className="flex items-center justify-center gap-2">
                  <Mail className="h-4 w-4" />
                  <span className="hidden sm:inline">Resend Confirmation</span>
                  <span className="sm:hidden">Resend</span>
                </Button>
                <Button variant="outline" onClick={() => handleDownloadInvoice(state.selectedBooking!.id)} disabled={actionLoading?.startsWith('invoice')} className="flex items-center justify-center gap-2">
                  <Download className="h-4 w-4" />
                  <span className="hidden sm:inline">Download Invoice</span>
                  <span className="sm:hidden">Download</span>
                </Button>
                <Button variant="outline" onClick={() => setIsDetailModalOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={confirmDialog.open}
        onOpenChange={(open) => setConfirmDialog(prev => ({ ...prev, open }))}
        title={confirmDialog.title}
        message={confirmDialog.message}
        variant={confirmDialog.variant}
        onConfirm={confirmDialog.action}
        loading={actionLoading !== null}
      />
    </Card>
  );
};

export { EnhancedBookingManagement };