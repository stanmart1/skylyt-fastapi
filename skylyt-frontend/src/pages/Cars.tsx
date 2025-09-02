import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Star, Users, Car, Filter, Eye } from 'lucide-react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { AdvancedSearch } from '@/components/search/AdvancedSearch';
import { useSearch } from '@/hooks/useSearch';
import { SearchParams } from '@/types/api';
import { ServerStatus } from '@/components/ServerStatus';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { useLocation } from 'react-router-dom';

const Cars = () => {
  const { cars, totalCars, isLoading, searchCars } = useSearch();
  const { currency } = useCurrency();
  const location = useLocation();
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [searchParams, setSearchParams] = useState<SearchParams>({});

  useEffect(() => {
    // Parse URL search parameters
    const urlParams = new URLSearchParams(location.search);
    const params: SearchParams = {
      page: 1,
      per_page: 20,
      currency
    };
    
    // Add search parameters from URL if they exist
    if (urlParams.get('location')) params.location = urlParams.get('location')!;
    if (urlParams.get('pickup_date')) params.pickup_date = urlParams.get('pickup_date')!;
    if (urlParams.get('return_date')) params.return_date = urlParams.get('return_date')!;
    
    setSearchParams(params);
    searchCars(params);
  }, [searchCars, currency, location.search]);

  const handleSearch = (params: SearchParams) => {
    setCurrentPage(1);
    searchCars({ ...params, page: 1, currency });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <header className="bg-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-800">Find Your Perfect Car</h1>
          <p className="text-gray-600">Discover amazing rental cars for your journey</p>
        </div>
      </header>

      <section className="container mx-auto px-4 py-8">
        <ServerStatus />
        
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
              <AdvancedSearch onSearch={handleSearch} type="car" />
            </div>
          </div>

          {/* Main Content - Car Listings */}
          <div className="flex-1 min-w-0">
            {/* Results Summary */}
            <div className="mb-6 flex justify-between items-center">
              <div>
                <p className="text-gray-600">
                  {isLoading ? 'Searching...' : `${totalCars} cars found`}
                </p>
                {searchParams.location && (
                  <p className="text-sm text-blue-600">
                    Location: {searchParams.location}
                    {searchParams.pickup_date && ` • From: ${searchParams.pickup_date}`}
                    {searchParams.return_date && ` • To: ${searchParams.return_date}`}
                  </p>
                )}
              </div>
              {totalCars > 0 && (
                <Badge variant="secondary">
                  Page {currentPage}
                </Badge>
              )}
            </div>

            {/* Car Grid */}
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-8">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-48 bg-gray-200 rounded-t-lg" />
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-3" />
                  <div className="flex gap-1 mb-4">
                    <div className="h-6 bg-gray-200 rounded w-12" />
                    <div className="h-6 bg-gray-200 rounded w-12" />
                    <div className="h-6 bg-gray-200 rounded w-12" />
                  </div>
                  <div className="flex justify-between">
                    <div className="h-6 bg-gray-200 rounded w-16" />
                    <div className="h-8 bg-gray-200 rounded w-20" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-8">
            {cars.map((car) => (
              <Card 
                key={car.id} 
                className="relative overflow-hidden hover:shadow-2xl hover:scale-105 transition-all duration-300 group cursor-pointer"
                onClick={() => {
                  console.log('Car clicked:', car);
                  if (car.id) {
                    window.location.href = `/car/${car.id}`;
                  }
                }}
              >
                <div className="relative">
                  <img
                    src={car.image_url || '/placeholder.svg'}
                    alt={car.name}
                    className="h-48 w-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  {/* Desktop Eye Icon - Centered */}
                  <div
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden lg:flex rounded-full w-14 h-14 shadow-lg items-center justify-center cursor-pointer z-20"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Eye clicked for car:', car);
                      if (car.id) {
                        window.location.href = `/car/${car.id}`;
                      }
                    }}
                  >
                    <Eye className="h-6 w-6 text-gray-900" />
                  </div>
                  {/* Overlay on hover */}
                  <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 hidden lg:block" />
                  <div className="absolute top-4 left-4">
                    <Badge className="bg-blue-600 text-white">
                      {car.category}
                    </Badge>
                  </div>
                </div>
                <CardContent className="p-6">
                    <h3 className="text-lg font-semibold mb-2">{car.name}</h3>

                    <div className="flex items-center text-gray-600 text-sm mb-3">
                      <Users className="h-4 w-4 mr-1" />
                      <span className="mr-4">{car.passengers} seats</span>
                      <Car className="h-4 w-4 mr-1" />
                      <span>{car.transmission}</span>
                    </div>

                    {car.features && car.features.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {car.features.slice(0, 3).map((feature) => (
                          <span key={feature} className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                            {feature}
                          </span>
                        ))}
                        {car.features.length > 3 && (
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                            +{car.features.length - 3}
                          </span>
                        )}
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <div>
                        <PriceDisplay 
                          amount={car.price_per_day || car.price} 
                          currency={car.currency || currency}
                          className="text-2xl font-bold text-blue-600"
                        />
                        <span className="text-gray-600 text-sm">/day</span>
                      </div>
                      <Button 
                        className="bg-orange-500 hover:bg-orange-600 text-white"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.location.href = `/booking?type=car&id=${car.id}`;
                        }}
                      >
                        Book Now
                      </Button>
                    </div>
                </CardContent>
              </Card>
            ))}
              </div>
            )}

            {cars.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <div className="max-w-md mx-auto">
                  <Car className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No cars found</h3>
                  <p className="text-gray-600 mb-4">Try adjusting your search criteria or browse our featured cars</p>
                  <Button onClick={() => handleSearch({ page: 1, per_page: 20 })} variant="outline">
                    Show All Cars
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Cars;
