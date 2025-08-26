export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string; // Computed field
  phone: string;
  phone_number?: string; // Alias for compatibility
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  roles: Role[];
}

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

export interface Permission {
  id: number;
  name: string;
  description: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  redirect_path?: string;
  user: User;
}

export interface Hotel {
  id: string;
  name: string;
  location: string;
  rating: number;
  price: number;
  image_url: string;
  amenities: string[];
  description: string;
}

export interface Car {
  id: string;
  name: string;
  category: string;
  price: number;
  image_url: string;
  passengers: number;
  transmission: string;
  features: string[];
}

export interface SearchParams {
  destination?: string;
  check_in?: string;
  check_out?: string;
  guests?: number;
  min_price?: number;
  max_price?: number;
  amenities?: string[];
  rating?: number;
  sort_by?: string;
  page?: number;
  per_page?: number;
}

export interface Booking {
  id: number;
  booking_reference: string;
  booking_type: 'hotel' | 'car' | 'bundle';
  status: 'pending' | 'confirmed' | 'cancelled';
  hotel_name?: string;
  car_name?: string;
  check_in_date?: string;
  check_out_date?: string;
  total_amount: number;
  currency: string;
  created_at: string;
}

export interface Payment {
  id: number;
  booking_id: number;
  gateway: 'stripe' | 'flutterwave' | 'paystack' | 'paypal' | 'bank_transfer';
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  transaction_id?: string;
}

export interface ApiError {
  detail: string;
  error_code?: string;
}