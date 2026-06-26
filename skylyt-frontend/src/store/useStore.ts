import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // Currency state
  currency: string;
  setCurrency: (currency: string) => void;
  
  // User preferences
  searchHistory: string[];
  addToSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
  
  // UI state
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  
  // Loading states
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Currency state
      currency: 'NGN',
      setCurrency: (currency) => set({ currency }),
      
      // User preferences
      searchHistory: [],
      addToSearchHistory: (query) => set((state) => ({
        searchHistory: [query, ...state.searchHistory.filter(q => q !== query)].slice(0, 10)
      })),
      clearSearchHistory: () => set({ searchHistory: [] }),
      
      // UI state
      sidebarOpen: false,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Loading states
      isLoading: false,
      setIsLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'skylyt-storage',
    }
  )
);