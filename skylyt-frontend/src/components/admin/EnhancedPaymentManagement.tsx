import React, { useEffect, useState } from 'react';
import { usePayment } from '../../contexts/PaymentContext';
import { Search, Filter, Download, Eye, RefreshCw, DollarSign, CreditCard } from 'lucide-react';
import PaymentDetailsModal from './PaymentDetailsModal';

const EnhancedPaymentManagement: React.FC = () => {
  const {
    state,
    fetchPayments,
    fetchPaymentStats,
    fetchPaymentDetails,
    verifyPayment,
    refundPayment,
    updatePaymentStatus,
    exportPayments,
    setFilters,
    resetFilters,
    setSelectedPayment,
  } = usePayment();

  const [showFilters, setShowFilters] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [refundForm, setRefundForm] = useState({ amount: 0, reason: '' });
  const [statusForm, setStatusForm] = useState({ status: '', notes: '' });
  const [filterForm, setFilterForm] = useState(state.filters);

  useEffect(() => {
    fetchPayments();
    fetchPaymentStats();
  }, []);

  useEffect(() => {
    fetchPayments(1);
  }, [state.filters]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters(filterForm);
    setShowFilters(false);
  };

  const handleRefund = async (e: React.FormEvent) => {
    e.preventDefault();
    if (state.selectedPayment) {
      await refundPayment(state.selectedPayment.id, refundForm.amount, refundForm.reason);
      setShowRefundModal(false);
      setRefundForm({ amount: 0, reason: '' });
    }
  };

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (state.selectedPayment) {
      await updatePaymentStatus(state.selectedPayment.id, statusForm.status, statusForm.notes);
      setShowStatusModal(false);
      setStatusForm({ status: '', notes: '' });
    }
  };

  const getStatusBadge = (status: string) => {
    const classes = {
      completed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
      refunded: 'bg-gray-100 text-gray-800',
    };
    return `px-2 py-1 rounded-full text-xs font-medium ${classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'}`;
  };

  const getProviderIcon = (provider: string) => {
    const icons = {
      stripe: '💳',
      paystack: '🟢',
      flutterwave: '🟡',
      paypal: '🔵',
      bank_transfer: '🏦',
    };
    return icons[provider as keyof typeof icons] || '💳';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Payment Management</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
          <button
            onClick={exportPayments}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-600 text-white rounded-lg hover:from-blue-700 hover:to-teal-700"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Stats */}
      {state.stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CreditCard className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Payments</p>
                <p className="text-2xl font-bold">{state.stats.total_payments}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Amount</p>
                <p className="text-2xl font-bold">${state.stats.total_amount.toFixed(2)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <RefreshCw className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold">{state.stats.pending_payments}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <Eye className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Failed</p>
                <p className="text-2xl font-bold">{state.stats.failed_payments}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleFilterSubmit} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={filterForm.status || ''}
                onChange={(e) => setFilterForm({ ...filterForm, status: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
                <option value="refunded">Refunded</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
              <select
                value={filterForm.provider || ''}
                onChange={(e) => setFilterForm({ ...filterForm, provider: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="">All Providers</option>
                <option value="stripe">Stripe</option>
                <option value="paystack">Paystack</option>
                <option value="flutterwave">Flutterwave</option>
                <option value="paypal">PayPal</option>
                <option value="bank_transfer">Bank Transfer</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
              <input
                type="date"
                value={filterForm.date_from || ''}
                onChange={(e) => setFilterForm({ ...filterForm, date_from: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
              <input
                type="date"
                value={filterForm.date_to || ''}
                onChange={(e) => setFilterForm({ ...filterForm, date_to: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                placeholder="Transaction ID, Guest..."
                value={filterForm.search || ''}
                onChange={(e) => setFilterForm({ ...filterForm, search: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div className="flex items-end space-x-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Apply
              </button>
              <button
                type="button"
                onClick={() => { resetFilters(); setFilterForm({}); }}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Payments Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {state.loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guest & Hotel</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {state.payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{payment.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{payment.booking.guest_name}</div>
                    <div className="text-sm text-gray-500">{payment.booking.hotel_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="mr-2">{getProviderIcon(payment.payment_method)}</span>
                      <span className="text-sm capitalize">{payment.payment_method}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {payment.currency} {payment.amount.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(payment.status)}>{payment.status}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(payment.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={async () => {
                          await fetchPaymentDetails(payment.id);
                          setShowDetailsModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => verifyPayment(payment.id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      {payment.status === 'completed' && (
                        <button
                          onClick={() => {
                            setSelectedPayment(payment);
                            setRefundForm({ amount: payment.amount, reason: '' });
                            setShowRefundModal(true);
                          }}
                          className="text-orange-600 hover:text-orange-900"
                        >
                          <DollarSign className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => {
                          setSelectedPayment(payment);
                          setStatusForm({ status: payment.status, notes: '' });
                          setShowStatusModal(true);
                        }}
                        className="text-purple-600 hover:text-purple-900"
                      >
                        <CreditCard className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {state.pagination.total_pages > 1 && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-700">
            Showing {((state.pagination.page - 1) * state.pagination.per_page) + 1} to{' '}
            {Math.min(state.pagination.page * state.pagination.per_page, state.pagination.total)} of{' '}
            {state.pagination.total} results
          </div>
          <div className="flex space-x-2">
            {Array.from({ length: state.pagination.total_pages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => fetchPayments(page)}
                className={`px-3 py-2 rounded-md ${
                  page === state.pagination.page
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {page}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Refund Modal */}
      {showRefundModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-medium mb-4">Process Refund</h3>
            <form onSubmit={handleRefund} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={refundForm.amount}
                  onChange={(e) => setRefundForm({ ...refundForm, amount: parseFloat(e.target.value) })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                <textarea
                  value={refundForm.reason}
                  onChange={(e) => setRefundForm({ ...refundForm, reason: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowRefundModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700"
                >
                  Process Refund
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Status Update Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-medium mb-4">Update Payment Status</h3>
            <form onSubmit={handleStatusUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={statusForm.status}
                  onChange={(e) => setStatusForm({ ...statusForm, status: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="refunded">Refunded</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={statusForm.notes}
                  onChange={(e) => setStatusForm({ ...statusForm, notes: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={3}
                  placeholder="Optional notes..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowStatusModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Update Status
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment Details Modal */}
      <PaymentDetailsModal
        payment={state.selectedPayment}
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        onUpdate={() => {
          fetchPayments();
          fetchPaymentStats();
        }}
      />
    </div>
  );
};

export default EnhancedPaymentManagement;