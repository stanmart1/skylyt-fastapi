import React, { createContext, useContext } from 'react';

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
  const features: Features = {
    car_rental_enabled: true,
    hotel_booking_enabled: true
  };

  return (
    <FeaturesContext.Provider value={{ features, loading: false, refreshFeatures: async () => {} }}>
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