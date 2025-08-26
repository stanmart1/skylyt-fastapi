import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Hotel, Car, Trash2 } from 'lucide-react';
import { useFavorites } from '@/hooks/useFavorites';

export const FavoritesManager = () => {
  const { favorites, isLoading, removeFavorite } = useFavorites();

  const getItemIcon = (itemType: string) => {
    switch (itemType) {
      case 'hotel': return Hotel;
      case 'car': return Car;
      default: return Heart;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            My Favorites
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-16 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-5 w-5" />
          My Favorites
        </CardTitle>
      </CardHeader>
      <CardContent>
        {favorites.length === 0 ? (
          <div className="text-center py-8">
            <Heart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No favorites yet</p>
            <p className="text-sm text-gray-500">Start adding hotels and cars to your favorites</p>
          </div>
        ) : (
          <div className="space-y-3">
            {favorites.map((favorite) => {
              const Icon = getItemIcon(favorite.item_type);
              return (
                <div key={favorite.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4 text-blue-600" />
                    <div>
                      <p className="font-medium">{favorite.name}</p>
                      <p className="text-sm text-gray-600 capitalize">{favorite.item_type}</p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeFavorite(favorite.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};