import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Star, MapPin, Eye, Heart } from 'lucide-react';
import { apiService } from '@/services/api';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { useFavorites } from '@/hooks/useFavorites';

const CityHotelsPage = () => {
  const { stateSlug, citySlug } = useParams();
  const { currency } = useCurrency();
  const { addToFavorites, removeFromFavorites, isFavorite } = useFavorites();
  const [state, setState] = useState<any>(null);
  const [city, setCity] = useState<any>(null);
  const [hotels, setHotels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCityHotels = async () => {
      try {
        const response = await apiService.request(`/destinations/${stateSlug}/${citySlug}/hotels?currency=${currency}`);
        setState(response.state);
        setCity(response.city);
        setHotels(response.hotels || []);
      } catch (error) {
        console.error('Failed to fetch city hotels:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (stateSlug && citySlug) {
      fetchCityHotels();
    }
  }, [stateSlug, citySlug, currency]);

  const handleFavoriteToggle = async (hotel: any) => {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/login';
      return;
    }
    
    if (isFavorite(hotel.id, 'hotel')) {
      await removeFromFavorites(hotel.id, 'hotel');
    } else {
      await addToFavorites({
        item_type: 'hotel',
        item_id: hotel.id,
        name: hotel.name
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="animate-pulse">
          <div className="h-32 bg-gray-200" />
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded-lg" />
              ))}
            </div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-8">
          <nav className="text-sm text-gray-600 mb-4">
            <a href="/" className="hover:text-blue-600">Home</a>
            <span className="mx-2">/</span>
            <a href="/destinations" className="hover:text-blue-600">Destinations</a>
            <span className="mx-2">/</span>
            <a href={`/destinations/${stateSlug}`} className="hover:text-blue-600">{state?.name}</a>
            <span className="mx-2">/</span>
            <span className="text-gray-900">{city?.name}</span>
          </nav>
          <h1 className="text-3xl font-bold mb-2">Hotels in {city?.name}</h1>
          <p className="text-gray-600">{hotels.length} hotels available</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {hotels.map((hotel: any) => (
            <Card
              key={hotel.id}
              className="relative overflow-hidden hover:shadow-2xl hover:scale-105 transition-all duration-300 group cursor-pointer"
              onClick={() => window.location.href = `/hotel/${hotel.id}`}
            >
              <div className="relative">
                <img
                  src={hotel.image_url || hotel.images?.[0] || '/placeholder.svg'}
                  alt={hotel.name}
                  className="h-48 w-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                {/* Desktop Eye Icon - Centered */}
                <div
                  className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden lg:flex rounded-full w-14 h-14 shadow-lg items-center justify-center cursor-pointer z-20"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    window.location.href = `/hotel/${hotel.id}`;
                  }}
                >
                  <Eye className="h-6 w-6 text-gray-900" />
                </div>
                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 hidden lg:block" />
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute top-2 right-2 bg-white/80 hover:bg-white z-10"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleFavoriteToggle(hotel);
                  }}
                >
                  <Heart className={`h-4 w-4 ${isFavorite(hotel.id, 'hotel') ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
                </Button>
              </div>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold truncate">{hotel.name}</h3>
                  <div className="flex items-center space-x-1 text-sm">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="font-medium">{hotel.rating || hotel.star_rating}</span>
                  </div>
                </div>
                <div className="flex items-center text-sm text-gray-600 mb-3">
                  <MapPin className="h-4 w-4 mr-1" />
                  <span className="truncate">{hotel.location}</span>
                </div>
                {hotel.description && (
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{hotel.description}</p>
                )}
                {hotel.amenities && hotel.amenities.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {hotel.amenities.slice(0, 3).map((amenity) => (
                      <Badge key={amenity} variant="secondary" className="text-xs">
                        {amenity}
                      </Badge>
                    ))}
                    {hotel.amenities.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{hotel.amenities.length - 3} more
                      </Badge>
                    )}
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <div>
                    <PriceDisplay 
                      amount={hotel.price || hotel.price_per_night} 
                      currency={hotel.currency || currency}
                      isNGNStored={false}
                      className="text-2xl font-bold text-blue-600"
                    />
                    <span className="text-gray-500 text-sm">/night</span>
                  </div>
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.location.href = `/booking?type=hotel&id=${hotel.id}`;
                    }}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Book Now
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {hotels.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No hotels found in {city?.name}.</p>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default CityHotelsPage;