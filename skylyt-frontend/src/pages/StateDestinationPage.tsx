import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MapPin, Hotel, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { apiService } from '@/services/api';

const StateDestinationPage = () => {
  const { stateSlug } = useParams();
  const [state, setState] = useState<any>(null);
  const [cities, setCities] = useState([]);
  const [filteredCities, setFilteredCities] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStateData = async () => {
      try {
        const response = await apiService.request(`/destinations/${stateSlug}`);
        setState(response.state);
        setCities(response.featured_cities || []);
        setFilteredCities(response.featured_cities || []);
      } catch (error) {
        console.error('Failed to fetch state data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (stateSlug) {
      fetchStateData();
    }
  }, [stateSlug]);

  useEffect(() => {
    const filtered = cities.filter((city: any) =>
      city.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    // Sort by hotel count (highest first)
    const sorted = filtered.sort((a: any, b: any) => b.hotel_count - a.hotel_count);
    setFilteredCities(sorted);
  }, [searchTerm, cities]);

  const handleCityClick = (citySlug: string) => {
    window.location.href = `/destinations/${stateSlug}/${citySlug}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="animate-pulse">
          <div className="h-64 bg-gray-200" />
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-48 bg-gray-200 rounded-lg" />
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
      
      {/* State Header */}
      <div className="relative h-64 overflow-hidden">
        <img
          src={state?.featured_image_url || '/placeholder.svg'}
          alt={state?.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />
        <div className="absolute inset-0 flex items-center justify-center text-white">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2">{state?.name}</h1>
            <p className="text-lg">{state?.hotel_count} hotels available</p>
          </div>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-3">
          <nav className="text-sm text-gray-600">
            <a href="/" className="hover:text-blue-600">Home</a>
            <span className="mx-2">/</span>
            <a href="/destinations" className="hover:text-blue-600">Destinations</a>
            <span className="mx-2">/</span>
            <span className="text-gray-900">{state?.name}</span>
          </nav>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Search Cities */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search cities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Cities Grid */}
        <div className="max-w-6xl mx-auto">
          {/* Top 2 Large Cards */}
          {filteredCities.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {filteredCities.slice(0, 2).map((city: any) => (
                <div
                  key={city.id}
                  className="relative h-64 rounded-xl overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
                  onClick={() => handleCityClick(city.slug)}
                >
                  {/* Background Image */}
                  <img
                    src={city.featured_image_url}
                    alt={city.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  
                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30 group-hover:from-black/70 group-hover:to-black/50 transition-all duration-300" />
                  
                  {/* Title with Flag */}
                  <div className="absolute top-4 left-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-2xl font-bold text-white">{city.name}</h3>
                      <span className="text-xl">🇳🇬</span>
                    </div>
                    <p className="text-white/90 text-lg mt-1">{city.hotel_count} hotels</p>
                  </div>
                  
                  {/* Glow Border for Popular Cities */}
                  {city.is_featured && (
                    <div className="absolute inset-0 rounded-xl border-2 border-orange-400 shadow-lg shadow-orange-400/50" />
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Smaller Cards for Remaining Cities */}
          {filteredCities.length > 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCities.slice(2).map((city: any) => (
                <div
                  key={city.id}
                  className="relative h-48 rounded-xl overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
                  onClick={() => handleCityClick(city.slug)}
                >
                  {/* Background Image */}
                  <img
                    src={city.featured_image_url}
                    alt={city.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  
                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30 group-hover:from-black/70 group-hover:to-black/50 transition-all duration-300" />
                  
                  {/* Title with Flag */}
                  <div className="absolute top-4 left-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold text-white">{city.name}</h3>
                      <span className="text-lg">🇳🇬</span>
                    </div>
                    <p className="text-white/90 text-sm mt-1">{city.hotel_count} hotels</p>
                  </div>
                  
                  {/* Glow Border for Popular Cities */}
                  {city.is_featured && (
                    <div className="absolute inset-0 rounded-xl border-2 border-orange-400 shadow-lg shadow-orange-400/50" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {filteredCities.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No cities found matching your search.</p>
          </div>
        )}

        {/* View All Hotels Button */}
        <div className="text-center mt-12">
          <Button
            onClick={() => window.location.href = `/destinations/${stateSlug}/hotels`}
            className="bg-blue-600 hover:bg-blue-700"
          >
            View All Hotels in {state?.name}
          </Button>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default StateDestinationPage;