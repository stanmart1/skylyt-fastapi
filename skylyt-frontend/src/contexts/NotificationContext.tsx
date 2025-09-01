import React, { createContext, useContext, useEffect, useState } from 'react';
import { oneSignalService } from '@/services/oneSignalService';

interface NotificationContextType {
  isInitialized: boolean;
  userId: string | null;
  sendNotification: (title: string, message: string, url?: string) => Promise<void>;
  sendToUser: (userId: string, title: string, message: string, url?: string) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    // Only initialize if we're in a browser environment
    if (typeof window !== 'undefined') {
      // Add a small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        initializeOneSignal();
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, []);

  const initializeOneSignal = async () => {
    try {
      const appId = import.meta.env.VITE_ONESIGNAL_APP_ID;
      
      if (!appId || appId === 'your-onesignal-app-id' || appId === 'undefined') {
        console.warn('OneSignal App ID not configured properly');
        setIsInitialized(false);
        return;
      }
      
      if (typeof window === 'undefined' || !('OneSignal' in window)) {
        console.warn('OneSignal SDK not loaded');
        setIsInitialized(false);
        return;
      }

      const OneSignal = (window as any).OneSignal;
      
      // Wait for OneSignal to be ready
      await OneSignal.init({
        appId: appId,
        allowLocalhostAsSecureOrigin: true,
        notifyButton: {
          enable: false,
        },
      });

      // Wait for initialization to complete
      await new Promise((resolve) => {
        OneSignal.on('ready', resolve);
        // Fallback timeout
        setTimeout(resolve, 3000);
      });

      // Try to get user ID using different methods
      let playerId = null;
      
      try {
        // Method 1: Modern API (if available)
        if (OneSignal.User && OneSignal.User.PushSubscription) {
          playerId = OneSignal.User.PushSubscription.id;
        }
      } catch (e) {
        console.debug('Modern API not available:', e);
      }
      
      try {
        // Method 2: Legacy API (fallback)
        if (!playerId && typeof OneSignal.getUserId === 'function') {
          playerId = await OneSignal.getUserId();
        }
      } catch (e) {
        console.debug('Legacy getUserId not available:', e);
      }
      
      try {
        // Method 3: Alternative legacy method
        if (!playerId && typeof OneSignal.getPlayerId === 'function') {
          playerId = await OneSignal.getPlayerId();
        }
      } catch (e) {
        console.debug('getPlayerId not available:', e);
      }

      setUserId(playerId);
      setIsInitialized(true);
      console.log('OneSignal initialized successfully', { playerId });
      
    } catch (error) {
      console.error('Failed to initialize OneSignal:', error);
      setIsInitialized(false);
      setUserId(null);
    }
  };

  const sendNotification = async (title: string, message: string, url?: string) => {
    try {
      return await oneSignalService.sendToAllUsers(title, message, url);
    } catch (error) {
      console.error('Failed to send notification:', error);
      throw error;
    }
  };

  const sendToUser = async (userId: string, title: string, message: string, url?: string) => {
    try {
      return await oneSignalService.sendToUser(userId, title, message, url);
    } catch (error) {
      console.error('Failed to send user notification:', error);
      throw error;
    }
  };

  return (
    <NotificationContext.Provider value={{
      isInitialized,
      userId,
      sendNotification,
      sendToUser,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};