import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Booking } from '@/types/api';

interface BookingState {
  bookings: Booking[];
  selectedBooking: Booking | null;
  loading: boolean;
  error: string | null;
  filters: {
    search: string;
    status: string;
    paymentStatus: string;
    bookingType: string;
    startDate: string;
    endDate: string;
    sortBy: string;
    sortOrder: string;
  };
  pagination: {
    page: number;
    perPage: number;
    total: number;
    totalPages: number;
  };
}

type BookingAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_BOOKINGS'; payload: { bookings: Booking[]; total: number; page: number; totalPages: number } }
  | { type: 'SET_SELECTED_BOOKING'; payload: Booking | null }
  | { type: 'UPDATE_BOOKING'; payload: Booking }
  | { type: 'DELETE_BOOKING'; payload: number }
  | { type: 'DELETE_BOOKINGS'; payload: number[] }
  | { type: 'SET_FILTERS'; payload: Partial<BookingState['filters']> }
  | { type: 'SET_PAGINATION'; payload: Partial<BookingState['pagination']> }
  | { type: 'RESET_FILTERS' };

const initialState: BookingState = {
  bookings: [],
  selectedBooking: null,
  loading: false,
  error: null,
  filters: {
    search: '',
    status: '',
    paymentStatus: '',
    bookingType: '',
    startDate: '',
    endDate: '',
    sortBy: 'created_at',
    sortOrder: 'desc'
  },
  pagination: {
    page: 1,
    perPage: 20,
    total: 0,
    totalPages: 0
  }
};

function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_BOOKINGS':
      return {
        ...state,
        bookings: action.payload.bookings,
        pagination: {
          ...state.pagination,
          total: action.payload.total,
          page: action.payload.page,
          totalPages: action.payload.totalPages
        },
        loading: false,
        error: null
      };
    
    case 'SET_SELECTED_BOOKING':
      return { ...state, selectedBooking: action.payload };
    
    case 'UPDATE_BOOKING':
      return {
        ...state,
        bookings: state.bookings.map(booking =>
          booking.id === action.payload.id ? action.payload : booking
        ),
        selectedBooking: state.selectedBooking?.id === action.payload.id ? action.payload : state.selectedBooking
      };
    
    case 'DELETE_BOOKING':
      return {
        ...state,
        bookings: state.bookings.filter(booking => booking.id !== action.payload),
        selectedBooking: state.selectedBooking?.id === action.payload ? null : state.selectedBooking
      };
    
    case 'DELETE_BOOKINGS':
      return {
        ...state,
        bookings: state.bookings.filter(booking => !action.payload.includes(booking.id)),
        selectedBooking: action.payload.includes(state.selectedBooking?.id || 0) ? null : state.selectedBooking
      };
    
    case 'SET_FILTERS':
      return {
        ...state,
        filters: { ...state.filters, ...action.payload },
        pagination: { ...state.pagination, page: 1 } // Reset to first page when filtering
      };
    
    case 'SET_PAGINATION':
      return {
        ...state,
        pagination: { ...state.pagination, ...action.payload }
      };
    
    case 'RESET_FILTERS':
      return {
        ...state,
        filters: initialState.filters,
        pagination: { ...initialState.pagination }
      };
    
    default:
      return state;
  }
}

interface BookingContextType {
  state: BookingState;
  dispatch: React.Dispatch<BookingAction>;
  actions: {
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    setBookings: (data: { bookings: Booking[]; total: number; page: number; totalPages: number }) => void;
    setSelectedBooking: (booking: Booking | null) => void;
    updateBooking: (booking: Booking) => void;
    deleteBooking: (id: number) => void;
    deleteBookings: (ids: number[]) => void;
    setFilters: (filters: Partial<BookingState['filters']>) => void;
    setPagination: (pagination: Partial<BookingState['pagination']>) => void;
    resetFilters: () => void;
  };
}

const BookingContext = createContext<BookingContextType | undefined>(undefined);

export function BookingProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(bookingReducer, initialState);

  const actions = {
    setLoading: (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }),
    setError: (error: string | null) => dispatch({ type: 'SET_ERROR', payload: error }),
    setBookings: (data: { bookings: Booking[]; total: number; page: number; totalPages: number }) => 
      dispatch({ type: 'SET_BOOKINGS', payload: data }),
    setSelectedBooking: (booking: Booking | null) => dispatch({ type: 'SET_SELECTED_BOOKING', payload: booking }),
    updateBooking: (booking: Booking) => dispatch({ type: 'UPDATE_BOOKING', payload: booking }),
    deleteBooking: (id: number) => dispatch({ type: 'DELETE_BOOKING', payload: id }),
    deleteBookings: (ids: number[]) => dispatch({ type: 'DELETE_BOOKINGS', payload: ids }),
    setFilters: (filters: Partial<BookingState['filters']>) => dispatch({ type: 'SET_FILTERS', payload: filters }),
    setPagination: (pagination: Partial<BookingState['pagination']>) => dispatch({ type: 'SET_PAGINATION', payload: pagination }),
    resetFilters: () => dispatch({ type: 'RESET_FILTERS' })
  };

  return (
    <BookingContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </BookingContext.Provider>
  );
}

export function useBooking() {
  const context = useContext(BookingContext);
  if (context === undefined) {
    throw new Error('useBooking must be used within a BookingProvider');
  }
  return context;
}