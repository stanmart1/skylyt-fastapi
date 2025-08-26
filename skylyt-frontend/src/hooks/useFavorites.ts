import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface Favorite {
  id: number;
  item_type: string;
  item_id: string;
  name: string;
  created_at: string;
}

export const useFavorites = () => {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const fetchFavorites = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getFavorites();
      const userFavorites = Array.isArray(response) ? response : response.favorites || [];
      setFavorites(userFavorites);
    } catch (error) {
      console.error('Favorites fetch error:', error);
      setFavorites([]);
      // Don't show error toast for unauthenticated users
    } finally {
      setIsLoading(false);
    }
  };

  const addFavorite = async (itemType: string, itemId: string, name: string) => {
    try {
      const newFavorite = await apiService.addFavorite({
        item_type: itemType,
        item_id: itemId,
        name: name,
      });
      setFavorites(prev => [...prev, newFavorite]);
      toast({
        title: 'Added to Favorites',
        description: `${name} has been added to your favorites.`,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to add to favorites.',
        variant: 'destructive',
      });
    }
  };

  const removeFavorite = async (favoriteId: number) => {
    try {
      await apiService.removeFavorite(favoriteId);
      setFavorites(prev => prev.filter(fav => fav.id !== favoriteId));
      toast({
        title: 'Removed from Favorites',
        description: 'Item has been removed from your favorites.',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to remove from favorites.',
        variant: 'destructive',
      });
    }
  };

  const isFavorite = (itemType: string, itemId: string) => {
    return favorites.some(fav => fav.item_type === itemType && fav.item_id === itemId);
  };

  useEffect(() => {
    // Only fetch favorites if user might be authenticated
    const token = localStorage.getItem('token');
    if (token) {
      fetchFavorites();
    }
  }, []);

  return {
    favorites,
    isLoading,
    addFavorite,
    removeFavorite,
    isFavorite,
  };
};