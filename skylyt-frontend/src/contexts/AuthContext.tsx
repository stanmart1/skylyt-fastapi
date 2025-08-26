import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types/api';
import { apiService } from '@/services/api';
import { ErrorHandler } from '@/utils/errorHandler';

interface AuthContextType {
  user: User | null;
  login: (credentials: LoginRequest) => Promise<{ success: boolean; redirectTo?: string }>;
  register: (userData: RegisterRequest) => Promise<boolean>;
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

  const login = async (credentials: LoginRequest): Promise<{ success: boolean; redirectTo?: string }> => {
    try {
      const response: TokenResponse = await apiService.login(credentials);
      
      apiService.setToken(response.access_token);
      setUser(response.user);
      
      // Use redirect_path from backend response or determine based on role
      const redirectTo = response.redirect_path || 
        (response.user.roles.some(role => role.name === 'admin' || role.name === 'superadmin') ? '/admin' : '/dashboard');
      
      return { success: true, redirectTo };
    } catch (error) {
      console.error('Login failed:', ErrorHandler.handle(error));
      return { success: false };
    }
  };

  const register = async (userData: RegisterRequest): Promise<boolean> => {
    try {
      await apiService.register(userData);
      return true;
    } catch (error) {
      console.error('Registration failed:', ErrorHandler.handle(error));
      return false;
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
