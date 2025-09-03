import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { apiService } from '@/services/api';
import { sanitizeForLogging, sanitizeForJson } from '@/utils/sanitize';

export interface Payment {
  id: number;
  booking_id: number;
  payment_method: string;
  amount: number;
  currency: string;
  status: string;
  transaction_id?: string;
  transfer_reference?: string;
  gateway_response?: any;
  created_at: string;
  updated_at: string;
  booking: {
    id: number;
    guest_name: string;
    hotel_name: string;
    check_in: string;
    check_out: string;
    status: string;
  };
}

export interface PaymentFilters {
  status?: string;
  provider?: string;
  date_from?: string;
  date_to?: string;
  amount_min?: number;
  amount_max?: number;
  search?: string;
}

export interface PaymentStats {
  total_payments: number;
  completed_payments: number;
  pending_payments: number;
  failed_payments: number;
  total_amount: number;
}

interface PaymentState {
  payments: Payment[];
  selectedPayment: Payment | null;
  filters: PaymentFilters;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
  stats: PaymentStats | null;
  loading: boolean;
  error: string | null;
}

type PaymentAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_PAYMENTS'; payload: { payments: Payment[]; pagination: any } }
  | { type: 'SET_SELECTED_PAYMENT'; payload: Payment | null }
  | { type: 'SET_FILTERS'; payload: PaymentFilters }
  | { type: 'SET_STATS'; payload: PaymentStats }
  | { type: 'UPDATE_PAYMENT'; payload: Payment }
  | { type: 'RESET_FILTERS' };

const initialState: PaymentState = {
  payments: [],
  selectedPayment: null,
  filters: {},
  pagination: {
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
  },
  stats: null,
  loading: false,
  error: null,
};

function paymentReducer(state: PaymentState, action: PaymentAction): PaymentState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_PAYMENTS':
      return {
        ...state,
        payments: action.payload.payments,
        pagination: action.payload.pagination,
        loading: false,
        error: null,
      };
    case 'SET_SELECTED_PAYMENT':
      return { ...state, selectedPayment: action.payload };
    case 'SET_FILTERS':
      return { ...state, filters: action.payload };
    case 'SET_STATS':
      return { ...state, stats: action.payload };
    case 'UPDATE_PAYMENT':
      return {
        ...state,
        payments: state.payments.map(p =>
          p.id === action.payload.id ? action.payload : p
        ),
        selectedPayment: state.selectedPayment?.id === action.payload.id
          ? action.payload
          : state.selectedPayment,
      };
    case 'RESET_FILTERS':
      return { ...state, filters: {} };
    default:
      return state;
  }
}

interface PaymentContextType {
  state: PaymentState;
  fetchPayments: (page?: number) => Promise<void>;
  fetchPaymentStats: () => Promise<void>;
  fetchPaymentDetails: (id: number) => Promise<void>;
  verifyPayment: (id: number) => Promise<void>;
  refundPayment: (id: number, amount: number, reason: string) => Promise<void>;
  updatePaymentStatus: (id: number, status: string, notes?: string) => Promise<void>;
  exportPayments: () => Promise<void>;
  initializePayment: (paymentData: any) => Promise<any>;
  setFilters: (filters: PaymentFilters) => void;
  resetFilters: () => void;
  setSelectedPayment: (payment: Payment | null) => void;
}

const PaymentContext = createContext<PaymentContextType | undefined>(undefined);

export function PaymentProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(paymentReducer, initialState);

  const fetchPayments = async (page = 1) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const sanitizedFilters = sanitizeForJson(state.filters);
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: state.pagination.per_page.toString(),
        ...Object.fromEntries(
          Object.entries(sanitizedFilters).filter(([_, v]) => v !== undefined && v !== '')
        ),
      });

      const data = await apiService.request(`/api/v1/payments?${params}`);
      dispatch({
        type: 'SET_PAYMENTS',
        payload: {
          payments: data.payments,
          pagination: {
            page: data.page,
            per_page: data.per_page,
            total: data.total,
            total_pages: data.total_pages,
          },
        },
      });
    } catch (error) {
      console.error('Failed to fetch payments:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch payments' });
    }
  };

  const fetchPaymentStats = async () => {
    try {
      const stats = await apiService.request('/api/v1/payments/stats');
      dispatch({ type: 'SET_STATS', payload: stats });
    } catch (error) {
      console.error('Failed to fetch payment stats:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch payment stats' });
    }
  };

  const fetchPaymentDetails = async (id: number) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const payment = await apiService.request(`/api/v1/payments/${id}`);
      dispatch({ type: 'SET_SELECTED_PAYMENT', payload: payment });
    } catch (error) {
      console.error('Failed to fetch payment details:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch payment details' });
    }
  };

  const verifyPayment = async (id: number) => {
    try {
      await apiService.request(`/api/v1/payments/${id}/verify`, {
        method: 'POST',
      });
      
      await fetchPaymentDetails(id);
      await fetchPayments(state.pagination.page);
    } catch (error) {
      console.error('Failed to verify payment:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to verify payment' });
    }
  };

  const refundPayment = async (id: number, amount: number, reason: string) => {
    try {
      await apiService.request(`/api/v1/payments/${id}/refund`, {
        method: 'POST',
        body: JSON.stringify({ amount, reason }),
      });
      
      await fetchPaymentDetails(id);
      await fetchPayments(state.pagination.page);
    } catch (error) {
      console.error('Failed to process refund:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to process refund' });
    }
  };

  const updatePaymentStatus = async (id: number, status: string, notes?: string) => {
    try {
      await apiService.request(`/api/v1/payments/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status, notes }),
      });
      
      await fetchPaymentDetails(id);
      await fetchPayments(state.pagination.page);
    } catch (error) {
      console.error('Failed to update payment status:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update payment status' });
    }
  };

  const exportPayments = async () => {
    try {
      const params = new URLSearchParams(
        Object.fromEntries(
          Object.entries(state.filters).filter(([_, v]) => v !== undefined && v !== '')
        )
      );

      const response = await fetch(`${apiService['baseURL']}/api/v1/payments/export/csv?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      if (!response.ok) throw new Error('Failed to export payments');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'payments_export.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export payments:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to export payments' });
    }
  };

  const setFilters = (filters: PaymentFilters) => {
    dispatch({ type: 'SET_FILTERS', payload: filters });
  };

  const resetFilters = () => {
    dispatch({ type: 'RESET_FILTERS' });
  };

  const setSelectedPayment = (payment: Payment | null) => {
    dispatch({ type: 'SET_SELECTED_PAYMENT', payload: payment });
  };

  const initializePayment = async (paymentData: any) => {
    try {
      const result = await apiService.initializePayment(paymentData);
      return result;
    } catch (error) {
      console.error('Failed to initialize payment:', sanitizeForLogging(error));
      dispatch({ type: 'SET_ERROR', payload: 'Failed to initialize payment' });
      throw error;
    }
  };

  return (
    <PaymentContext.Provider
      value={{
        state,
        fetchPayments,
        fetchPaymentStats,
        fetchPaymentDetails,
        verifyPayment,
        refundPayment,
        updatePaymentStatus,
        exportPayments,
        initializePayment,
        setFilters,
        resetFilters,
        setSelectedPayment,
      }}
    >
      {children}
    </PaymentContext.Provider>
  );
}

export function usePayment() {
  const context = useContext(PaymentContext);
  if (context === undefined) {
    throw new Error('usePayment must be used within a PaymentProvider');
  }
  return context;
}