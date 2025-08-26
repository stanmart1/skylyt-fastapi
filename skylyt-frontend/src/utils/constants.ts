export const API_BASE_URL = 'https://skylytapi.scaleitpro.com/api/v1';

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  USERS: {
    ME: '/users/me',
    BOOKINGS: '/users/me/bookings',
    FAVORITES: '/users/me/favorites',
  },
  HOTELS: {
    SEARCH: '/hotels/search',
    DETAILS: '/hotels',
    DESTINATIONS: '/hotels/destinations',
    AMENITIES: '/hotels/amenities',
  },
  CARS: {
    SEARCH: '/cars/search',
    DETAILS: '/cars',
    LOCATIONS: '/cars/locations',
    CATEGORIES: '/cars/categories',
  },
  BOOKINGS: {
    CREATE: '/bookings',
    LIST: '/bookings',
    DETAILS: '/bookings',
    CANCEL: '/bookings',
  },
  PAYMENTS: {
    PROCESS: '/payments/process',
    STATUS: '/payments',
    REFUND: '/payments',
    WEBHOOK: '/payments/webhook',
  },
  SEARCH: {
    BUNDLES: '/search/bundles',
    COMPARE: '/search/compare',
    SUGGESTIONS: '/search/suggestions',
    HISTORY: '/search/history',
  },
} as const;

export const PAYMENT_GATEWAYS = {
  STRIPE: 'stripe',
  FLUTTERWAVE: 'flutterwave',
  PAYSTACK: 'paystack',
  PAYPAL: 'paypal',
  BANK_TRANSFER: 'bank_transfer',
} as const;

export const BOOKING_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  CANCELLED: 'cancelled',
} as const;

export const ROLES = {
  SUPERADMIN: 'superadmin',
  ADMIN: 'admin',
  ACCOUNTANT: 'accountant',
  CUSTOMER: 'customer',
} as const;