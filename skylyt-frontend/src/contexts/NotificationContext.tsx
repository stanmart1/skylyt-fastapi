import React, { createContext, useContext } from 'react';

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
  const sendNotification = async (title: string, message: string, url?: string) => {
    console.log('In-app notification:', { title, message, url });
  };

  const sendToUser = async (userId: string, title: string, message: string, url?: string) => {
    console.log('In-app user notification:', { userId, title, message, url });
  };

  return (
    <NotificationContext.Provider value={{
      isInitialized: true,
      userId: null,
      sendNotification,
      sendToUser,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};