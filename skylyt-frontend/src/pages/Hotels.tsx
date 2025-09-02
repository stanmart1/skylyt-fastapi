import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Star, Heart, MapPin, Filter, Eye } from 'lucide-react';
import { AdvancedSearch } from '@/components/search/AdvancedSearch';
import { useSearch } from '@/hooks/useSearch';
import { useFavorites } from '@/hooks/useFavorites';
import { SearchParams } from '@/types/api';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { SearchResultsSkeleton } from '@/components/LoadingStates';
import { ServerStatus } from '@/components/ServerStatus';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const Hotels = () => {
  const { hotels, totalHotels, isLoading, searchHotels } = useSearch();
  const { addToFavorites, removeFromFavorites, isFavorite } = useFavorites();
  const { currency } = useCurrency();
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [searchParams, setSearchParams] = useState<SearchParams>({});

  useEffect(() => {
    // Parse URL search parameters
    const urlParams = new URLSearchParams(location.search);
    const params: SearchParams = {
      page: 1,
      per_page: 50,
      currency
    };
    
    // Add search parameters from URL if they exist
    if (urlParams.get('destination')) params.destination = urlParams.get('destination')!;
    if (urlParams.get('checkin_date')) params.checkin_date = urlParams.get('checkin_date')!;
    if (urlParams.get('checkout_date')) params.checkout_date = urlParams.get('checkout_date')!;
    
    setSearchParams(params);
    searchHotels(params);
  }, [searchHotels, currency, location.search]);

  const handleSearch = (params: SearchParams) => {
    setCurrentPage(1);
    searchHotels({ ...params, page: 1, currency });
  };

  const handleFavoriteToggle = async (hotel: any) => {
    if (!isAuthenticated) {
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <header className="bg-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-800">Find Your Perfect Hotel</h1>
          <p className="text-gray-600">Discover amazing hotels for your next trip</p>
        </div>
      </header>

      <section className="container mx-auto px-4 py-8">
        <ServerStatus />
        <ErrorBoundary>
          {/* Mobile Filter Toggle */}
          <div className="lg:hidden mb-4">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 w-full justify-center"
            >
              <Filter className="h-4 w-4" />
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </Button>
          </div>

          <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
            {/* Left Sidebar - Filters */}
            <div className={`w-full lg:w-80 lg:flex-shrink-0 ${showFilters ? 'block' : 'hidden lg:block'}`}>
              <div className="lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-y-auto">
                <AdvancedSearch onSearch={handleSearch} type="hotel" />
              </div>
            </div>

            {/* Main Content - Hotel Listings */}
            <div className="flex-1 min-w-0">
              {/* Results Summary */}
              <div className="mb-6 flex justify-between items-center">
                <div>
                  <p className="text-gray-600">
                    {isLoading ? 'Searching...' : `${totalHotels} hotels found`}
                  </p>
                  {searchParams.destination && (
                    <p className="text-sm text-blue-600">
                      Destination: {searchParams.destination}
                      {searchParams.checkin_date && ` • Check-in: ${searchParams.checkin_date}`}
                      {searchParams.checkout_date && ` • Check-out: ${searchParams.checkout_date}`}
                    </p>
                  )}
                </div>
                {totalHotels > 0 && (
                  <Badge variant="secondary">
                    Page {currentPage}
                  </Badge>
                )}
              </div>

              {/* Hotel Listings */}
              {isLoading ? (
                <SearchResultsSkeleton />
              ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-8">
                {hotels.map((hotel) => (
                  <Card 
                    key={hotel.id} 
                    className="relative overflow-hidden hover:shadow-2xl hover:scale-105 transition-all duration-300 group cursor-pointer"
                    onClick={() => window.location.href = `/hotel/${hotel.id}`}
                  >
                    <div className="relative">
                      <img 
                        src={hotel.image_url || '/placeholder.svg'} 
                        alt={hotel.name} 
                        className="h-48 w-full object-cover group-hover:scale-110 transition-transform duration-500" 
                      />
                      {/* Desktop Eye Icon - Centered */}
                      <div
                        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden lg:flex rounded-full w-14 h-14 shadow-lg items-center justify-center cursor-pointer z-20"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          console.log('Eye clicked for hotel:', hotel.id);
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
                    <CardHeader>
                      <CardTitle className="flex items-start justify-between">
                        <span className="truncate">{hotel.name}</span>
                        <div className="flex items-center space-x-1 text-sm">
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          <span className="font-medium">{hotel.rating}</span>
                        </div>
                      </CardTitle>
                      <div className="flex items-center text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mr-1" />
                        <span className="truncate">{hotel.location}</span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">{hotel.description}</p>
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
                            amount={hotel.price} 
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
            )}

            {hotels.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <div className="max-w-md mx-auto">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No hotels found</h3>
                  <p className="text-gray-600 mb-4">Try adjusting your search criteria or browse our featured hotels</p>
                  <Button onClick={() => handleSearch({ page: 1, per_page: 20 })} variant="outline">
                    Show All Hotels
                  </Button>
                </div>
              </div>
            )}
            </div>
          </div>
        </ErrorBoundary>
      </section>
      
      <Footer />
    </div>
  );
};

export default Hotels;
