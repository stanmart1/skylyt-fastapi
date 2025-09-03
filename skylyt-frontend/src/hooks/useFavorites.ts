import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { sanitizeForLogging, sanitizeForJson } from '@/utils/sanitize';

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
      const userFavorites = Array.isArray(response) ? response : [];
      setFavorites(userFavorites);
    } catch (error) {
      console.error('Favorites fetch error:', sanitizeForLogging(error));
      setFavorites([]);
      // Don't show error toast for unauthenticated users
    } finally {
      setIsLoading(false);
    }
  };

  const addFavorite = async (itemType: string, itemId: string, name: string) => {
    try {
      const sanitizedData = sanitizeForJson({
        item_type: itemType,
        item_id: itemId,
        name: name,
      });
      const response = await apiService.addFavorite(sanitizedData);
      // Refresh favorites list after adding
      await fetchFavorites();
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

  const isFavorite = (itemId: string, itemType: string) => {
    return favorites.some(fav => fav.item_type === itemType && fav.item_id === itemId);
  };
  
  const addToFavorites = async (favoriteData: { item_type: string; item_id: string; name: string }) => {
    return addFavorite(favoriteData.item_type, favoriteData.item_id, favoriteData.name);
  };
  
  const removeFromFavorites = async (itemId: string, itemType: string) => {
    const favorite = favorites.find(fav => fav.item_type === itemType && fav.item_id === itemId);
    if (favorite) {
      return removeFavorite(favorite.id);
    }
  };

  useEffect(() => {
    // Only fetch favorites if user might be authenticated
    const token = localStorage.getItem('access_token');
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
    addToFavorites,
    removeFromFavorites,
  };
};