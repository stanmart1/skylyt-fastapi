import { ApiError } from '@/types/api';

export class ErrorHandler {
  static handle(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }
    
    if (typeof error === 'string') {
      return error;
    }
    
    return 'An unexpected error occurred';
  }

  static handleApiError(error: ApiError): string {
    switch (error.error_code) {
      case 'PAYMENT_FAILED':
        return 'Payment processing failed. Please try again or use a different payment method.';
      case 'BOOKING_UNAVAILABLE':
        return 'This booking is no longer available. Please search for alternatives.';
      case 'INVALID_CREDENTIALS':
        return 'Invalid email or password. Please check your credentials.';
      case 'USER_NOT_FOUND':
        return 'User account not found. Please register or check your email.';
      case 'INSUFFICIENT_PERMISSIONS':
        return 'You do not have permission to perform this action.';
      case 'RATE_LIMIT_EXCEEDED':
        return 'Too many requests. Please wait a moment and try again.';
      default:
        return error.detail || 'An error occurred. Please try again.';
    }
  }

  static isNetworkError(error: unknown): boolean {
    return error instanceof TypeError && error.message.includes('fetch');
  }

  static shouldRetry(error: unknown): boolean {
    if (this.isNetworkError(error)) return true;
    
    if (error instanceof Error) {
      const retryableMessages = ['timeout', 'network', 'connection'];
      return retryableMessages.some(msg => 
        error.message.toLowerCase().includes(msg)
      );
    }
    
    return false;
  }
}