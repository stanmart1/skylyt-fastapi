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
  const [addPaymentModalOpen, setAddPaymentModalOpen] = useState(false);
  const [addPaymentForm, setAddPaymentForm] = useState({
    booking_id: '',
    amount: '',
    payment_method: 'bank_transfer',
    payment_reference: '',
    transaction_id: '',
    notes: '',
    // Bank transfer specific fields
    transfer_reference: '',
    proof_of_payment: null as File | null,
    // Gateway specific fields
    gateway_reference: '',
    customer_email: ''
  });
  const [availablePaymentMethods, setAvailablePaymentMethods] = useState([]);
  const [loadingPaymentMethods, setLoadingPaymentMethods] = useState(false);
  const { hasPermission } = useAuth();
  const { currency } = useCurrency();

  useEffect(() => {
    fetchPayments();
    fetchAvailablePaymentMethods();
  }, []);

  const fetchAvailablePaymentMethods = async () => {
    try {
      setLoadingPaymentMethods(true);
      const response = await apiService.request('/payment-config/gateways');
      
      // Always include bank transfer and basic methods
      const basicMethods = [
        { id: 'bank_transfer', name: 'Bank Transfer', description: 'Direct bank transfer' },
        { id: 'stripe', name: 'Stripe', description: 'Credit/Debit Cards' },
        { id: 'paystack', name: 'Paystack', description: 'Nigerian Payment Gateway' },
        { id: 'flutterwave', name: 'Flutterwave', description: 'African Payment Gateway' },
        { id: 'paypal', name: 'PayPal', description: 'PayPal Account' }
      ];
      
      // If API returns configured gateways, merge with basic methods
      if (response.success && response.gateways) {
        const configuredGateways = response.gateways.map(gateway => ({
          id: gateway.id,
          name: gateway.name,
          description: gateway.description
        }));
        
        // Merge configured with basic, preferring configured data
        const mergedMethods = basicMethods.map(basic => {
          const configured = configuredGateways.find(c => c.id === basic.id);
          return configured || basic;
        });
        
        setAvailablePaymentMethods(mergedMethods);
      } else {
        // Use basic methods as fallback
        setAvailablePaymentMethods(basicMethods);
      }
    } catch (error) {
      console.error('Failed to fetch payment methods:', error);
      // Fallback to basic methods
      setAvailablePaymentMethods([
        { id: 'bank_transfer', name: 'Bank Transfer', description: 'Direct bank transfer' },
        { id: 'stripe', name: 'Stripe', description: 'Credit/Debit Cards' },
        { id: 'paystack', name: 'Paystack', description: 'Nigerian Payment Gateway' },
        { id: 'flutterwave', name: 'Flutterwave', description: 'African Payment Gateway' },
        { id: 'paypal', name: 'PayPal', description: 'PayPal Account' }
      ]);
    } finally {
      setLoadingPaymentMethods(false);
    }
  };

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

  const handleAddPayment = async () => {
    try {
      setUpdating(true);
      
      const formData = new FormData();
      formData.append('booking_id', addPaymentForm.booking_id);
      formData.append('amount', addPaymentForm.amount);
      formData.append('payment_method', addPaymentForm.payment_method);
      formData.append('payment_reference', addPaymentForm.payment_reference);
      formData.append('notes', addPaymentForm.notes);
      formData.append('status', 'completed');
      
      // Add method-specific fields
      if (addPaymentForm.payment_method === 'bank_transfer') {
        if (addPaymentForm.transfer_reference) {
          formData.append('transfer_reference', addPaymentForm.transfer_reference);
        }
        if (addPaymentForm.proof_of_payment) {
          formData.append('proof_of_payment', addPaymentForm.proof_of_payment);
        }
      } else {
        // For gateway payments
        if (addPaymentForm.transaction_id) {
          formData.append('transaction_id', addPaymentForm.transaction_id);
        }
        if (addPaymentForm.gateway_reference) {
          formData.append('gateway_reference', addPaymentForm.gateway_reference);
        }
        if (addPaymentForm.customer_email) {
          formData.append('customer_email', addPaymentForm.customer_email);
        }
      }
      
      await apiService.request('/admin/payments/manual', {
        method: 'POST',
        body: formData,
        headers: {} // Let browser set content-type for FormData
      });
      
      await fetchPayments();
      setAddPaymentModalOpen(false);
      setAddPaymentForm({
        booking_id: '',
        amount: '',
        payment_method: 'bank_transfer',
        payment_reference: '',
        transaction_id: '',
        notes: '',
        transfer_reference: '',
        proof_of_payment: null,
        gateway_reference: '',
        customer_email: ''
      });
    } catch (error) {
      console.error('Failed to add payment:', error);
      alert('Failed to add payment record. Please try again.');
    } finally {
      setUpdating(false);
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
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              {bookingType === 'hotel' ? 'Hotel Payment Records' : 
               bookingType === 'car' ? 'Car Payment Records' : 
               'Payment Records'}
            </CardTitle>
            {hasPermission('payments.create') && (
              <Button onClick={() => setAddPaymentModalOpen(true)} className="w-full sm:w-auto">
                <Plus className="h-4 w-4 mr-2" />
                Add Payment Record
              </Button>
            )}
          </div>
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

      {/* Add Payment Modal */}
      <Dialog open={addPaymentModalOpen} onOpenChange={setAddPaymentModalOpen}>
        <DialogContent className="w-full max-w-md mx-4 sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add Manual Payment Record</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="booking_id">Booking ID</Label>
                <Input
                  id="booking_id"
                  type="number"
                  value={addPaymentForm.booking_id}
                  onChange={(e) => setAddPaymentForm({ ...addPaymentForm, booking_id: e.target.value })}
                  placeholder="Enter booking ID"
                />
              </div>
              <div>
                <Label htmlFor="amount">Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={addPaymentForm.amount}
                  onChange={(e) => setAddPaymentForm({ ...addPaymentForm, amount: e.target.value })}
                  placeholder="Enter payment amount"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="payment_method">Payment Method</Label>
              {loadingPaymentMethods ? (
                <div className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Loading payment methods...
                </div>
              ) : (
                <select
                  id="payment_method"
                  value={addPaymentForm.payment_method}
                  onChange={(e) => setAddPaymentForm({ ...addPaymentForm, payment_method: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {availablePaymentMethods.map((method) => (
                    <option key={method.id} value={method.id}>
                      {method.name} - {method.description}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Bank Transfer Specific Fields */}
            {addPaymentForm.payment_method === 'bank_transfer' && (
              <div className="space-y-4 p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-semibold text-green-800">Bank Transfer Details</h4>
                <div>
                  <Label htmlFor="transfer_reference">Transfer Reference</Label>
                  <Input
                    id="transfer_reference"
                    value={addPaymentForm.transfer_reference}
                    onChange={(e) => setAddPaymentForm({ ...addPaymentForm, transfer_reference: e.target.value })}
                    placeholder="Bank transfer reference number"
                  />
                </div>
                <div>
                  <Label htmlFor="proof_of_payment">Proof of Payment</Label>
                  <Input
                    id="proof_of_payment"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null;
                      setAddPaymentForm({ ...addPaymentForm, proof_of_payment: file });
                    }}
                    className="cursor-pointer"
                  />
                  <p className="text-xs text-gray-500 mt-1">Upload receipt, screenshot, or PDF</p>
                </div>
              </div>
            )}

            {/* Gateway Payment Specific Fields */}
            {addPaymentForm.payment_method !== 'bank_transfer' && (
              <div className="space-y-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-blue-800">
                  {availablePaymentMethods.find(m => m.id === addPaymentForm.payment_method)?.name || 'Gateway'} Payment Details
                </h4>
                <div>
                  <Label htmlFor="transaction_id">Transaction ID</Label>
                  <Input
                    id="transaction_id"
                    value={addPaymentForm.transaction_id}
                    onChange={(e) => setAddPaymentForm({ ...addPaymentForm, transaction_id: e.target.value })}
                    placeholder="Gateway transaction ID"
                  />
                </div>
                <div>
                  <Label htmlFor="gateway_reference">Gateway Reference</Label>
                  <Input
                    id="gateway_reference"
                    value={addPaymentForm.gateway_reference}
                    onChange={(e) => setAddPaymentForm({ ...addPaymentForm, gateway_reference: e.target.value })}
                    placeholder="Gateway reference number"
                  />
                </div>
                <div>
                  <Label htmlFor="customer_email">Customer Email</Label>
                  <Input
                    id="customer_email"
                    type="email"
                    value={addPaymentForm.customer_email}
                    onChange={(e) => setAddPaymentForm({ ...addPaymentForm, customer_email: e.target.value })}
                    placeholder="Customer email address"
                  />
                </div>
              </div>
            )}

            <div>
              <Label htmlFor="payment_reference">Payment Reference</Label>
              <Input
                id="payment_reference"
                value={addPaymentForm.payment_reference}
                onChange={(e) => setAddPaymentForm({ ...addPaymentForm, payment_reference: e.target.value })}
                placeholder="General payment reference"
              />
            </div>
            
            <div>
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Input
                id="notes"
                value={addPaymentForm.notes}
                onChange={(e) => setAddPaymentForm({ ...addPaymentForm, notes: e.target.value })}
                placeholder="Additional notes"
              />
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 pt-4">
              <Button 
                onClick={handleAddPayment} 
                disabled={updating || !addPaymentForm.booking_id || !addPaymentForm.amount} 
                className="w-full sm:w-auto"
              >
                {updating ? 'Adding...' : 'Add Payment'}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setAddPaymentModalOpen(false);
                  setAddPaymentForm({
                    booking_id: '',
                    amount: '',
                    payment_method: 'bank_transfer',
                    payment_reference: '',
                    transaction_id: '',
                    notes: '',
                    transfer_reference: '',
                    proof_of_payment: null,
                    gateway_reference: '',
                    customer_email: ''
                  });
                }} 
                className="w-full sm:w-auto"
              >
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