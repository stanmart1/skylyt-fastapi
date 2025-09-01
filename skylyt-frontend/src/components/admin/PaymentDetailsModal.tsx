import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { 
  ExternalLink, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Download, 
  Eye,
  DollarSign,
  Calendar,
  User,
  Building,
  CreditCard
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';

interface PaymentDetailsModalProps {
  payment: any;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

const PaymentDetailsModal = ({ payment, isOpen, onClose, onUpdate }: PaymentDetailsModalProps) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [refundAmount, setRefundAmount] = useState('');
  const [refundReason, setRefundReason] = useState('');
  const [statusUpdate, setStatusUpdate] = useState('');
  const [statusNotes, setStatusNotes] = useState('');

  const handleVerifyPayment = async () => {
    setLoading(true);
    try {
      await apiService.request(`/payments/${payment.id}/verify`, { method: 'POST' });
      toast({ title: "Payment verified successfully" });
      onUpdate();
    } catch (error) {
      toast({ title: "Verification failed", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleRefund = async () => {
    if (!refundAmount || !refundReason) {
      toast({ title: "Please fill in refund details", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      await apiService.request(`/payments/${payment.id}/refund`, {
        method: 'POST',
        body: JSON.stringify({
          amount: parseFloat(refundAmount),
          reason: refundReason
        })
      });
      toast({ title: "Refund processed successfully" });
      onUpdate();
      setRefundAmount('');
      setRefundReason('');
    } catch (error) {
      toast({ title: "Refund failed", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!statusUpdate) {
      toast({ title: "Please select a status", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      await apiService.request(`/payments/${payment.id}/status`, {
        method: 'PUT',
        body: JSON.stringify({
          status: statusUpdate,
          notes: statusNotes
        })
      });
      toast({ title: "Status updated successfully" });
      onUpdate();
      setStatusUpdate('');
      setStatusNotes('');
    } catch (error) {
      toast({ title: "Status update failed", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const viewProofOfPayment = () => {
    if (payment.proof_of_payment_url) {
      window.open(`${import.meta.env.VITE_API_BASE_URL}/api/v1/payments/proof/${payment.id}`, '_blank');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'refunded': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!payment) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Payment Details - #{payment.id}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* General Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-4 w-4" />
                General Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Booking Reference:</span>
                <Button 
                  variant="link" 
                  className="p-0 h-auto"
                  onClick={() => window.open(`/admin/bookings/${payment.booking_id}`, '_blank')}
                >
                  #{payment.booking_id} <ExternalLink className="h-3 w-3 ml-1" />
                </Button>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Customer Name:</span>
                <span className="font-medium">{payment.customer_name || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Customer Email:</span>
                <span className="font-medium">{payment.customer_email || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Service Type:</span>
                <span className="font-medium capitalize">{payment.booking?.service_type || 'N/A'}</span>
              </div>
              {payment.booking?.hotel_name && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Hotel:</span>
                  <span className="font-medium">{payment.booking.hotel_name}</span>
                </div>
              )}
              {payment.booking?.car_name && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Car:</span>
                  <span className="font-medium">{payment.booking.car_name}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Transaction Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Transaction Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Payment Method:</span>
                <Badge variant="outline" className="capitalize">
                  {payment.payment_method.replace('_', ' ')}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Amount Paid:</span>
                <span className="font-bold text-lg">${payment.amount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Currency:</span>
                <span className="font-medium">{payment.currency}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <Badge className={getStatusColor(payment.status)}>
                  {payment.status}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Transaction ID:</span>
                <span className="font-medium text-xs">{payment.transaction_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Payment Reference:</span>
                <span className="font-medium text-xs">{payment.payment_reference || 'N/A'}</span>
              </div>
            </CardContent>
          </Card>

          {/* Timestamps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Created:</span>
                <span className="font-medium">
                  {new Date(payment.created_at).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated:</span>
                <span className="font-medium">
                  {new Date(payment.updated_at).toLocaleString()}
                </span>
              </div>
              {payment.refund_date && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Refund Date:</span>
                  <span className="font-medium">
                    {new Date(payment.refund_date).toLocaleString()}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Refund Information */}
          <Card>
            <CardHeader>
              <CardTitle>Refund Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Refund Status:</span>
                <Badge variant="outline">{payment.refund_status || 'none'}</Badge>
              </div>
              {payment.refund_amount && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Refund Amount:</span>
                  <span className="font-medium">${payment.refund_amount}</span>
                </div>
              )}
              {payment.refund_reason && (
                <div>
                  <span className="text-gray-600">Refund Reason:</span>
                  <p className="text-sm mt-1">{payment.refund_reason}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Admin Actions */}
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-semibold">Admin Actions</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button onClick={handleVerifyPayment} disabled={loading} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Verify Payment
            </Button>
            
            {payment.proof_of_payment_url && (
              <Button onClick={viewProofOfPayment} variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                View Proof
              </Button>
            )}
            
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Download Invoice
            </Button>
            
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Download Receipt
            </Button>
          </div>

          {/* Refund Section */}
          {payment.status === 'completed' && payment.refund_status !== 'full' && (
            <Card>
              <CardHeader>
                <CardTitle>Issue Refund</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="refund-amount">Refund Amount</Label>
                    <Input
                      id="refund-amount"
                      type="number"
                      placeholder="0.00"
                      value={refundAmount}
                      onChange={(e) => setRefundAmount(e.target.value)}
                      max={payment.amount}
                    />
                  </div>
                  <div>
                    <Label htmlFor="refund-reason">Reason</Label>
                    <Input
                      id="refund-reason"
                      placeholder="Refund reason"
                      value={refundReason}
                      onChange={(e) => setRefundReason(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={handleRefund} disabled={loading} variant="destructive">
                  Process Refund
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Status Update Section */}
          <Card>
            <CardHeader>
              <CardTitle>Update Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="status-update">New Status</Label>
                  <select
                    id="status-update"
                    className="w-full p-2 border rounded"
                    value={statusUpdate}
                    onChange={(e) => setStatusUpdate(e.target.value)}
                  >
                    <option value="">Select status</option>
                    <option value="pending">Pending</option>
                    <option value="processing">Processing</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="refunded">Refunded</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="status-notes">Notes</Label>
                  <Textarea
                    id="status-notes"
                    placeholder="Admin notes"
                    value={statusNotes}
                    onChange={(e) => setStatusNotes(e.target.value)}
                  />
                </div>
              </div>
              <Button onClick={handleStatusUpdate} disabled={loading}>
                Update Status
              </Button>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaymentDetailsModal;