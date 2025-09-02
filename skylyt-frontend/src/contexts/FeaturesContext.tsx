import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '@/services/api';

interface Features {
  car_rental_enabled: boolean;
  hotel_booking_enabled: boolean;
}

interface FeaturesContextType {
  features: Features;
  loading: boolean;
  refreshFeatures: () => Promise<void>;
}

const FeaturesContext = createContext<FeaturesContextType | undefined>(undefined);

export const FeaturesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [features, setFeatures] = useState<Features>({
    car_rental_enabled: true,
    hotel_booking_enabled: true
  });
  const [loading, setLoading] = useState(true);

  const fetchFeatures = async () => {
    try {
      const response = await apiService.request('/config/features');
      setFeatures(response);
    } catch (error) {
      console.error('Failed to fetch features:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeatures();
  }, []);

  return (
    <FeaturesContext.Provider value={{ features, loading, refreshFeatures: fetchFeatures }}>
      {children}
    </FeaturesContext.Provider>
  );
};

export const useFeatures = () => {
  const context = useContext(FeaturesContext);
  if (!context) {
    throw new Error('useFeatures must be used within FeaturesProvider');
  }
  return context;
};