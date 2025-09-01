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
    initializeOneSignal();
  }, []);

  const initializeOneSignal = async () => {
    try {
      const appId = import.meta.env.VITE_ONESIGNAL_APP_ID;
      
      if (!appId || appId === 'your-onesignal-app-id') {
        console.warn('OneSignal App ID not configured');
        return;
      }
      
      if (typeof window !== 'undefined' && 'OneSignal' in window) {
        await (window as any).OneSignal.init({
          appId: appId,
          allowLocalhostAsSecureOrigin: true,
        });

        // Use modern OneSignal API
        const playerId = await (window as any).OneSignal.User.PushSubscription.id;
        setUserId(playerId);
        setIsInitialized(true);
      }
    } catch (error) {
      console.error('Failed to initialize OneSignal:', error);
      // Set as initialized even if getting player ID fails
      setIsInitialized(true);
    }
  };

  const sendNotification = async (title: string, message: string, url?: string) => {
    return oneSignalService.sendToAllUsers(title, message, url);
  };

  const sendToUser = async (userId: string, title: string, message: string, url?: string) => {
    return oneSignalService.sendToUser(userId, title, message, url);
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