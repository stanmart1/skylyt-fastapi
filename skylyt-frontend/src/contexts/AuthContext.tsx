import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types/api';
import { apiService } from '@/services/api';
import { ErrorHandler } from '@/utils/errorHandler';

interface AuthContextType {
  user: User | null;
  login: (credentials: LoginRequest) => Promise<{ success: boolean; redirectTo?: string; error?: string }>;
  register: (userData: RegisterRequest) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        apiService.setToken(token);
        try {
          const currentUser = await apiService.getCurrentUser();
          setUser(currentUser);
          
          // Handle persistent routing after reload
          const currentPath = window.location.pathname;
          const isAdmin = currentUser.roles.some(role => role.name === 'admin' || role.name === 'superadmin');
          
          // Redirect admins to admin dashboard if they're on regular dashboard
          if (isAdmin && currentPath === '/dashboard') {
            window.location.replace('/admin');
          }
          // Redirect non-admins away from admin dashboard
          else if (!isAdmin && currentPath.startsWith('/admin')) {
            window.location.replace('/dashboard');
          }
        } catch (error) {
          console.error('Failed to get current user:', error);
          apiService.clearToken();
          localStorage.removeItem('access_token');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest): Promise<{ success: boolean; redirectTo?: string; error?: string }> => {
    try {
      const response: TokenResponse = await apiService.login(credentials);
      
      apiService.setToken(response.access_token);
      setUser(response.user);
      
      // Use redirect_path from backend response or determine based on role
      const redirectTo = response.redirect_path || 
        (response.user.roles.some(role => role.name === 'admin' || role.name === 'superadmin') ? '/admin' : '/dashboard');
      
      return { success: true, redirectTo };
    } catch (error: any) {
      console.error('Login failed:', error);
      
      let errorMessage = "Login failed. Please try again.";
      
      if (error.message) {
        if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('Invalid credentials')) {
          errorMessage = "Invalid email or password. Please check your credentials.";
        } else if (error.message.includes('404') || error.message.includes('User not found')) {
          errorMessage = "No account found with this email address.";
        } else if (error.message.includes('403') || error.message.includes('Account disabled')) {
          errorMessage = "Your account has been disabled. Please contact support.";
        } else if (error.message.includes('429') || error.message.includes('Too many')) {
          errorMessage = "Too many login attempts. Please wait before trying again.";
        } else if (error.message.includes('network') || error.message.includes('fetch') || error.message.includes('connect')) {
          errorMessage = "Unable to connect to server. Please check your connection.";
        } else if (error.message.includes('timeout')) {
          errorMessage = "Request timed out. Please try again.";
        } else {
          errorMessage = error.message;
        }
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData: RegisterRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      await apiService.register(userData);
      return { success: true };
    } catch (error: any) {
      console.error('Registration failed:', error);
      
      let errorMessage = "Registration failed. Please try again.";
      
      if (error.message) {
        if (error.message.includes('already exists') || error.message.includes('already registered')) {
          errorMessage = "An account with this email already exists. Please use a different email or try logging in.";
        } else if (error.message.includes('invalid email') || error.message.includes('email format')) {
          errorMessage = "Please enter a valid email address.";
        } else if (error.message.includes('password') && error.message.includes('weak')) {
          errorMessage = "Password is too weak. Please use a stronger password with at least 8 characters.";
        } else if (error.message.includes('validation') || error.message.includes('required')) {
          errorMessage = "Please fill in all required fields correctly.";
        } else if (error.message.includes('network') || error.message.includes('fetch')) {
          errorMessage = "Unable to connect to server. Please check your connection.";
        } else {
          errorMessage = error.message;
        }
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    setUser(null);
    apiService.clearToken();
    localStorage.removeItem('access_token');
    window.location.href = '/';
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    
    return user.roles.some(role => 
      role.permissions.some(p => p.name === permission)
    );
  };

  const hasRole = (roleName: string): boolean => {
    if (!user) return false;
    
    return user.roles.some(role => role.name === roleName);
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isLoading,
    hasPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
