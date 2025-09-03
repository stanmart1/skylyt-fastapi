import { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  TokenResponse, 
  Hotel, 
  Car, 
  SearchParams, 
  Booking, 
  Payment,
  ApiError 
} from '@/types/api';

class ApiService {
  private baseURL = import.meta.env.VITE_API_BASE_URL;
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        let errorMessage = 'API request failed';
        try {
          const error: ApiError = await response.json();
          // Sanitize error message to prevent XSS
          const sanitizedDetail = typeof error.detail === 'string' ? 
            error.detail.replace(/[<>"'&]/g, '') : 'API request failed';
          errorMessage = sanitizedDetail || 'API request failed';
        } catch {
          // Provide more specific error messages based on status codes
          switch (response.status) {
            case 401:
              errorMessage = 'Invalid credentials or session expired';
              break;
            case 403:
              errorMessage = 'Access denied - insufficient permissions';
              break;
            case 404:
              errorMessage = 'Resource not found';
              break;
            case 422:
              errorMessage = 'Invalid data provided';
              break;
            case 429:
              errorMessage = 'Too many requests - please wait before trying again';
              break;
            case 500:
              errorMessage = 'Server error - please try again later';
              break;
            case 503:
              errorMessage = 'Service temporarily unavailable';
              break;
            default:
              errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          }
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async formRequest<T>(
    endpoint: string, 
    data: Record<string, string>
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const formData = new URLSearchParams(data);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Request failed';
        try {
          const error: ApiError = await response.json();
          errorMessage = error.detail || 'Request failed';
        } catch {
          if (response.status === 401) {
            errorMessage = 'Invalid credentials';
          } else if (response.status === 422) {
            errorMessage = 'Invalid login data provided';
          } else {
            errorMessage = `Login failed (${response.status})`;
          }
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check your internet connection.');
      }
      throw error;
    }
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<TokenResponse> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request('/users/me');
  }

  // Hotels
  async searchHotels(params: SearchParams & { currency?: string }): Promise<{ hotels: Hotel[]; total: number }> {
    const queryString = new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key] = String(value);
        }
        return acc;
      }, {} as Record<string, string>)
    ).toString();

    return this.request(`/hotels/search?${queryString}`);
  }

  async getHotel(id: string): Promise<Hotel> {
    return this.request(`/hotels/${id}`);
  }

  // Cars
  async searchCars(params: SearchParams): Promise<{ cars: Car[]; total: number }> {
    const queryString = new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key] = String(value);
        }
        return acc;
      }, {} as Record<string, string>)
    ).toString();

    return this.request(`/cars/search?${queryString}`);
  }

  async getCar(id: string): Promise<Car> {
    return this.request(`/cars/${id}`);
  }

  // Bookings
  async createBooking(bookingData: Partial<Booking>): Promise<Booking> {
    return this.request('/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  }

  async createAdminBooking(bookingData: any): Promise<any> {
    return this.request('/admin/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  }

  async getBookings(): Promise<Booking[]> {
    return this.request('/bookings');
  }

  async getBooking(id: number): Promise<Booking> {
    return this.request(`/bookings/${id}`);
  }

  async cancelBooking(id: number): Promise<Booking> {
    return this.request(`/bookings/${id}`, {
      method: 'DELETE',
    });
  }

  // Payments
  async processPayment(paymentData: Partial<Payment>): Promise<Payment> {
    return this.request('/payments/process', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  }

  async initializePayment(paymentData: { 
    booking_id: number; 
    payment_method: string; 
    payment_reference?: string;
    amount?: number;
    currency?: string;
    gateway?: string;
    transfer_date?: string;
    notes?: string;
  }): Promise<any> {
    return this.request('/payments/initialize', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  }

  async getPayment(id: number): Promise<Payment> {
    return this.request(`/payments/${id}`);
  }

  // Favorites
  async getFavorites(): Promise<any[]> {
    return this.request('/users/me/favorites');
  }

  async addFavorite(itemData: { item_type: string; item_id: string; name: string }): Promise<any> {
    return this.request('/users/me/favorites', {
      method: 'POST',
      body: JSON.stringify(itemData),
    });
  }

  async removeFavorite(id: number): Promise<void> {
    return this.request(`/users/me/favorites/${id}`, {
      method: 'DELETE',
    });
  }

  // Profile Management
  async updateProfile(profileData: Partial<User>): Promise<User> {
    return this.request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData: { current_password: string; new_password: string }): Promise<void> {
    return this.request('/users/me/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  // Admin Methods
  async getUsers(): Promise<User[]> {
    return this.request('/rbac/users');
  }

  async updateUserRole(userId: number, roleId: number): Promise<void> {
    return this.request(`/rbac/users/${userId}/roles`, {
      method: 'POST',
      body: JSON.stringify({ role_id: roleId }),
    });
  }

  async updateUser(userId: number, userData: any): Promise<any> {
    return this.request(`/rbac/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId: number): Promise<void> {
    return this.request(`/rbac/users/${userId}`, {
      method: 'DELETE',
    });
  }

  async getAllBookings(params?: {
    search?: string;
    status?: string;
    paymentStatus?: string;
    bookingType?: string;
    startDate?: string;
    endDate?: string;
    sortBy?: string;
    sortOrder?: string;
    page?: number;
    perPage?: number;
  }): Promise<{ bookings: Booking[]; total: number; page: number; totalPages: number }> {
    const queryString = params ? new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          acc[key] = String(value);
        }
        return acc;
      }, {} as Record<string, string>)
    ).toString() : '';
    
    return this.request(`/admin/bookings${queryString ? '?' + queryString : ''}`);
  }

  async getBookingDetails(id: number): Promise<Booking> {
    return this.request(`/admin/bookings/${id}`);
  }

  async resendBookingConfirmation(id: number): Promise<void> {
    return this.request(`/admin/bookings/${id}/resend-confirmation`, {
      method: 'POST'
    });
  }

  async getBookingInvoice(id: number): Promise<any> {
    return this.request(`/admin/bookings/${id}/invoice`);
  }

  async cancelBookingAdmin(id: number, reason: string): Promise<void> {
    return this.request(`/admin/bookings/${id}/cancel`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
  }

  async updateBookingStatus(id: number, status: string): Promise<void> {
    return this.request(`/bookings/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  async verifyPayment(paymentId: number): Promise<void> {
    return this.request(`/admin/payments/${paymentId}/verify`, {
      method: 'POST',
    });
  }

  // Analytics
  async getAnalytics(range: string = '6m'): Promise<any> {
    return this.request(`/analytics/dashboard?range=${range}`);
  }

  async getAdminStats(): Promise<any> {
    return this.request('/admin/stats');
  }

  // Notifications
  async getNotifications(): Promise<any[]> {
    return this.request('/notifications');
  }

  async markNotificationRead(id: string): Promise<void> {
    return this.request(`/notifications/${id}/read`, {
      method: 'POST',
    });
  }

  // File Upload
  async uploadFile(formData: FormData): Promise<{ url: string; filename: string }> {
    const response = await fetch(`${this.baseURL}/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  }

  // Payment Proof Upload
  async uploadPaymentProof(bookingId: number, paymentReference: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('booking_id', bookingId.toString());
    formData.append('payment_reference', paymentReference);
    formData.append('file', file);
    
    try {
      const response = await fetch(`${this.baseURL}/payments/upload-proof`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw error;
    }
  }

  // Get Payment Proof
  async getPaymentProof(paymentId: number): Promise<any> {
    return this.request(`/payments/${paymentId}/proof`);
  }

  // Request Refund
  async requestRefund(paymentId: number, refundData: { amount?: number; reason?: string }): Promise<any> {
    return this.request(`/payments/refund/${paymentId}`, {
      method: 'POST',
      body: JSON.stringify(refundData),
    });
  }

  // Get Bank Transfer Details
  async getBankTransferDetails(): Promise<any> {
    return this.request('/bank-accounts');
  }

  // Complete Payment
  async completePayment(bookingId: number): Promise<any> {
    return this.request(`/payments/complete/${bookingId}`, {
      method: 'POST',
    });
  }

  // Bank Transfer Settings
  async getBankTransferSettings(): Promise<any> {
    return this.request('/settings/');
  }

  async updateBankTransferSettings(settingsData: {
    bank_name: string;
    account_name: string;
    account_number: string;
    is_primary_account: boolean;
  }): Promise<any> {
    return this.request('/settings/bank-transfer', {
      method: 'PUT',
      body: JSON.stringify(settingsData),
    });
  }



  // Complete Booking
  async completeBooking(bookingId: number): Promise<any> {
    return this.request(`/bookings/${bookingId}/complete`, {
      method: 'POST',
    });
  }

  // Update Booking
  async updateBooking(bookingId: number, updateData: any): Promise<any> {
    return this.request(`/bookings/${bookingId}/update`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  // Advanced Search
  async advancedSearch(params: SearchParams & {
    location?: string;
    category?: string;
    features?: string[];
  }): Promise<{ results: (Hotel | Car)[]; total: number; facets: any }> {
    const queryString = new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            acc[key] = value.join(',');
          } else {
            acc[key] = String(value);
          }
        }
        return acc;
      }, {} as Record<string, string>)
    ).toString();

    return this.request(`/search/advanced?${queryString}`);
  }

  // RBAC
  async getRoles(): Promise<any[]> {
    return this.request('/rbac/roles');
  }

  async getPermissions(): Promise<any[]> {
    return this.request('/rbac/permissions');
  }

  async createRole(roleData: { name: string; permissions: number[] }): Promise<any> {
    return this.request('/rbac/roles', {
      method: 'POST',
      body: JSON.stringify(roleData),
    });
  }

  // System Health
  async getSystemHealth(): Promise<any> {
    return this.request('/health');
  }

  async getAdminSystemHealth(): Promise<any> {
    return this.request('/admin/system/health');
  }

  // Generic upload method
  async upload(endpoint: string, formData: FormData): Promise<any> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  // Hotel Images
  async getHotelImages(hotelId: number): Promise<any> {
    return this.request(`/hotel-images/${hotelId}`);
  }

  async uploadHotelImages(formData: FormData): Promise<any> {
    return this.upload('/hotel-images/upload', formData);
  }

  async uploadHotelImageFromUrl(hotelId: number, imageUrl: string): Promise<any> {
    const formData = new FormData();
    formData.append('hotel_id', hotelId.toString());
    formData.append('image_url', imageUrl);
    return this.upload('/hotel-images/upload-url', formData);
  }

  async setHotelImageAsCover(imageId: number): Promise<any> {
    return this.request(`/hotel-images/${imageId}/cover`, { method: 'PUT' });
  }

  async deleteHotelImage(imageId: number): Promise<any> {
    return this.request(`/hotel-images/${imageId}`, { method: 'DELETE' });
  }

  async reorderHotelImages(imageOrders: Array<{id: number, order: number}>): Promise<any> {
    return this.request('/hotel-images/reorder', {
      method: 'PUT',
      body: JSON.stringify(imageOrders)
    });
  }

  // Localization
  async detectLocation(): Promise<any> {
    return this.request('/localization/detect');
  }

  async getSupportedCountries(): Promise<any> {
    return this.request('/localization/countries');
  }

  async convertCurrency(amount: number, fromCurrency: string, toCurrency: string): Promise<any> {
    return this.request(`/localization/convert/${amount}/${fromCurrency}/${toCurrency}`);
  }

  // Notifications
  async sendPushNotification(data: {
    title: string;
    message: string;
    userIds?: string[];
    segments?: string[];
    url?: string;
  }): Promise<any> {
    return this.request('/notifications/push', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Currency Rate Management
  async getCurrencyRates(): Promise<any[]> {
    return this.request('/admin/currency-rates');
  }

  async updateCurrencyRate(rateId: number, rate: number): Promise<any> {
    return this.request(`/admin/currency-rates/${rateId}`, {
      method: 'PUT',
      body: JSON.stringify({ rate })
    });
  }

  async convertCurrency(amount: number, fromCurrency: string, toCurrency: string): Promise<any> {
    return this.request(`/admin/currency-rates/convert/${amount}/${fromCurrency}/${toCurrency}`);
  }

  // Helper method to get full image URL
  getImageUrl(imagePath: string): string {
    if (!imagePath) return '';
    if (imagePath.startsWith('http')) return imagePath;
    return `${import.meta.env.VITE_API_BASE_URL}${imagePath.startsWith('/') ? imagePath : '/' + imagePath}`;
  }
}

export const apiService = new ApiService();