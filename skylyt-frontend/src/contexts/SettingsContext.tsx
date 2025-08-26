import React, { createContext, useContext, useState, useEffect } from 'react';

interface SettingsData {
  id: number;
  site_name: string;
  site_description: string;
  contact_email: string;
  contact_phone: string;
  maintenance_mode: boolean;
  password_min_length: string;
  session_timeout: string;
  two_factor_enabled: boolean;
  login_attempts_limit: string;
}

interface SettingsContextType {
  settings: SettingsData | null;
  loading: boolean;
  refreshSettings: () => Promise<void>;
  updateSettings: (newSettings: Partial<SettingsData>) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      setSettings(data);
      
      // Update document title
      if (data.site_name) {
        document.title = data.site_name;
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = (newSettings: Partial<SettingsData>) => {
    if (settings) {
      const updatedSettings = { ...settings, ...newSettings };
      setSettings(updatedSettings);
      
      // Update document title if site name changed
      if (newSettings.site_name) {
        document.title = newSettings.site_name;
      }
    }
  };

  useEffect(() => {
    refreshSettings();
  }, []);

  const value = {
    settings,
    loading,
    refreshSettings,
    updateSettings,
  };

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
};