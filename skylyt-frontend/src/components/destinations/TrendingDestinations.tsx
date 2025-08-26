import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { apiService } from '@/services/api';

const TrendingDestinations = () => {
  const [cities, setCities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPopularDestinations = async () => {
      try {
        const response = await apiService.request('/destinations/lagos/cities');
        const sortedCities = (response.cities || []).sort((a: any, b: any) => b.hotel_count - a.hotel_count);
        setCities(sortedCities);
      } catch (error) {
        console.error('Failed to fetch popular destinations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPopularDestinations();
  }, []);

  const handleCityClick = (citySlug: string) => {
    window.location.href = `/destinations/lagos/${citySlug}`;
  };

  if (isLoading) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Popular Destinations</h2>
            <p className="text-gray-600">Explore Lagos neighborhoods with amazing hotels</p>
          </div>
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-64 bg-gray-200 rounded-xl" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-48 bg-gray-200 rounded-xl" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Popular Destinations</h2>
          <p className="text-gray-600">Explore Lagos neighborhoods with amazing hotels</p>
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Top 2 Large Cards */}
          {cities.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {cities.slice(0, 2).map((city: any) => (
                <div
                  key={city.id}
                  className="relative h-64 rounded-xl overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
                  onClick={() => handleCityClick(city.slug)}
                >
                  <img
                    src={city.featured_image_url}
                    alt={city.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30" />
                  <div className="absolute top-4 left-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-2xl font-bold text-white">{city.name}</h3>
                      <span className="text-xl">🇳🇬</span>
                    </div>
                    <p className="text-white/90 text-lg mt-1">{city.hotel_count} hotels</p>
                  </div>
                  {city.is_featured && (
                    <div className="absolute inset-0 rounded-xl border-2 border-orange-400 shadow-lg shadow-orange-400/50" />
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Smaller Cards for Remaining Cities */}
          {cities.length > 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cities.slice(2).map((city: any) => (
                <div
                  key={city.id}
                  className="relative h-48 rounded-xl overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
                  onClick={() => handleCityClick(city.slug)}
                >
                  <img
                    src={city.featured_image_url}
                    alt={city.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30" />
                  <div className="absolute top-4 left-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold text-white">{city.name}</h3>
                      <span className="text-lg">🇳🇬</span>
                    </div>
                    <p className="text-white/90 text-sm mt-1">{city.hotel_count} hotels</p>
                  </div>
                  {city.is_featured && (
                    <div className="absolute inset-0 rounded-xl border-2 border-orange-400 shadow-lg shadow-orange-400/50" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="text-center mt-12">
          <Button 
            variant="outline"
            className="border-blue-600 text-blue-600 hover:bg-gradient-to-r hover:from-blue-600 hover:to-teal-600 hover:text-white px-8 py-4 text-lg"
            onClick={() => window.location.href = '/hotels'}
          >
            View All Hotels
          </Button>
        </div>
      </div>
    </section>
  );
};

export default TrendingDestinations;