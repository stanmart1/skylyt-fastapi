import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { toast } from '@/hooks/use-toast';

interface Notification {
  id: string;
  type: 'booking' | 'payment' | 'system';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotifications: () => void;
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
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated || !user) return;

    // Disable WebSocket for now - backend doesn't support it yet
    // const ws = new WebSocket(`ws://localhost:8002/ws/notifications/${user.id}`);
    
    // WebSocket functionality disabled
    // ws.onmessage = (event) => {
    //   const notification: Notification = JSON.parse(event.data);
    //   setNotifications(prev => [notification, ...prev]);
    //   
    //   toast({
    //     title: notification.title,
    //     description: notification.message,
    //   });
    // };

    // return () => ws.close();
  }, [isAuthenticated, user]);

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      markAsRead,
      markAllAsRead,
      clearNotifications,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};