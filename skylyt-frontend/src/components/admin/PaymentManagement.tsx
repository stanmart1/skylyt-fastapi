import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CreditCard, CheckCircle, Edit, Trash2, Plus } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface Payment {
  id: number;
  booking_id: number;
  amount: number;
  currency: string;
  status: string;
  payment_method: string;
  payment_reference?: string;
  proof_of_payment_url?: string;
  customer_name?: string;
  created_at: string;
  transaction_id?: string;
  transfer_reference?: string;
  booking?: {
    booking_reference: string;
    booking_type: string;
    hotel_name?: string;
    car_name?: string;
    customer_name: string;
  };
}

interface PaymentManagementProps {
  bookingType?: 'hotel' | 'car';
}

const PaymentManagement = ({ bookingType }: PaymentManagementProps = {}) => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [editForm, setEditForm] = useState({ status: '', transaction_id: '' });
  const [updating, setUpdating] = useState(false);
  const { hasPermission } = useAuth();
  const { currency } = useCurrency();

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      let endpoint = '/payments';
      if (bookingType === 'hotel') {
        endpoint = '/payments/hotel-payments';
      } else if (bookingType === 'car') {
        endpoint = '/payments/car-payments';
      }
      
      const data = await apiService.request(endpoint);
      setPayments(Array.isArray(data) ? data : Array.isArray(data?.payments) ? data.payments : []);
    } catch (error) {
      console.error('Failed to fetch payments:', error);
      setPayments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPayment = async (paymentId: number) => {
    try {
      setUpdating(true);
      await apiService.request(`/payments/${paymentId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: 'completed' })
      });
      await fetchPayments();
    } catch (error) {
      console.error('Failed to verify payment:', error);
      alert('Failed to verify payment. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleEditPayment = (payment: Payment) => {
    setSelectedPayment(payment);
    setEditForm({ status: payment.status, transaction_id: payment.transaction_id || '' });
    setEditModalOpen(true);
  };

  const handleUpdatePayment = async () => {
    if (!selectedPayment) return;
    
    try {
      setUpdating(true);
      await apiService.request(`/payments/${selectedPayment.id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: editForm.status })
      });
      await fetchPayments();
      setEditModalOpen(false);
    } catch (error) {
      console.error('Failed to update payment:', error);
      alert('Failed to update payment. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeletePayment = async (paymentId: number) => {
    try {
      await apiService.request(`/admin/payments/${paymentId}`, { method: 'DELETE' });
      await fetchPayments();
    } catch (error) {
      console.error('Failed to delete payment:', error);
      alert('Failed to delete payment. Please try again.');
    }
  };

  const handleProcessRefund = async (paymentId: number, amount?: number) => {
    try {
      setUpdating(true);
      await apiService.request(`/admin/payments/${paymentId}/refund`, {
        method: 'POST',
        body: JSON.stringify({ amount })
      });
      await fetchPayments();
    } catch (error) {
      console.error('Failed to process refund:', error);
      alert('Failed to process refund. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleExportPayments = async () => {
    try {
      const exportData = await apiService.request('/admin/payments/export');
      // Create and download CSV
      const csvContent = exportData.csv;
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `payments-export-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export payments:', error);
      alert('Failed to export payments. Please try again.');
    }
  };

  const handleTrackCommission = async (paymentId: number) => {
    try {
      const commissionData = await apiService.request(`/admin/payments/${paymentId}/commission`);
      alert(`Commission: ${commissionData.commission_amount} ${commissionData.currency} (${commissionData.commission_rate}%)`);
    } catch (error) {
      console.error('Failed to fetch commission data:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'refunded': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Payment Verification</CardTitle>
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
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            {bookingType === 'hotel' ? 'Hotel Payment Records' : 
             bookingType === 'car' ? 'Car Payment Records' : 
             'Payment Records'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
              ))}
            </div>
          ) : payments.length === 0 ? (
            <div className="text-center py-8">
              <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No payments found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Array.isArray(payments) && payments.map((payment) => (
                <div key={payment.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <CreditCard className="h-5 w-5 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold">
                          Payment #{payment.id}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Booking: #{payment.booking?.booking_reference || payment.booking_id}
                        </p>
                        {payment.booking?.hotel_name && (
                          <p className="text-sm text-gray-600">
                            Hotel: {payment.booking.hotel_name}
                          </p>
                        )}
                        {payment.booking?.car_name && (
                          <p className="text-sm text-gray-600">
                            Car: {payment.booking.car_name}
                          </p>
                        )}
                        <p className="text-sm text-gray-600">
                          Customer: {payment.customer_name || payment.booking?.customer_name}
                        </p>
                        <p className="text-sm text-gray-600">
                          Amount: <PriceDisplay amount={payment.amount} currency={payment.currency} />
                        </p>
                        <p className="text-sm text-gray-600">
                          Method: {payment.payment_method.replace('_', ' ')}
                        </p>
                        {payment.payment_reference && (
                          <p className="text-sm text-gray-600">
                            Reference: {payment.payment_reference}
                          </p>
                        )}
                        {payment.transaction_id && (
                          <p className="text-sm text-gray-600">
                            Transaction: {payment.transaction_id}
                          </p>
                        )}
                        {payment.proof_of_payment_url && (
                          <p className="text-sm text-blue-600">
                            <a href={`/api/v1/payments/proof/${payment.id}`} target="_blank" rel="noopener noreferrer">
                              View Proof of Payment
                            </a>
                          </p>
                        )}
                        <p className="text-xs text-gray-500">
                          {payment.created_at ? new Date(payment.created_at).toLocaleString() : 'No date'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(payment.status)}>
                        {payment.status}
                      </Badge>
                      {hasPermission('payments.update') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditPayment(payment)}
                          disabled={updating}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                      )}
                      {(payment.status === 'pending' || payment.payment_method === 'bank_transfer') && hasPermission('payments.verify') && (
                        <Button
                          size="sm"
                          onClick={() => handleVerifyPayment(payment.id)}
                          disabled={updating}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
                          {payment.payment_method === 'bank_transfer' ? 'Approve' : 'Verify'}
                        </Button>
                      )}
                      {hasPermission('payments.delete') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeletePayment(payment.id)}
                          className="text-red-600 hover:text-red-700"
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
      </Card>

      {/* Edit Payment Modal */}
      <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Payment #{selectedPayment?.id}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                value={editForm.status}
                onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="refunded">Refunded</option>
              </select>
            </div>
            <div>
              <Label htmlFor="transaction_id">Transaction ID</Label>
              <Input
                id="transaction_id"
                value={editForm.transaction_id}
                onChange={(e) => setEditForm({ ...editForm, transaction_id: e.target.value })}
                placeholder="Enter transaction ID"
              />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleUpdatePayment} disabled={updating}>
                {updating ? 'Updating...' : 'Update Payment'}
              </Button>
              <Button variant="outline" onClick={() => setEditModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export { PaymentManagement };