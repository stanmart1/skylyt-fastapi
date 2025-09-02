import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { MapPin, Search } from 'lucide-react';
import { apiService } from '@/services/api';

const Destinations = () => {
  const [states, setStates] = useState([]);
  const [filteredStates, setFilteredStates] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        const response = await apiService.request('/destinations');
        setStates(response.states || []);
        setFilteredStates(response.states || []);
      } catch (error) {
        console.error('Failed to fetch destinations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDestinations();
  }, []);

  useEffect(() => {
    const filtered = states.filter((state: any) =>
      state.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredStates(filtered);
  }, [searchTerm, states]);

  const handleStateClick = (stateSlug: string) => {
    window.location.href = `/destinations/${stateSlug}`;
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
      
      {/* Header */}
      <div className="relative h-64 overflow-hidden">
        <img
          src="/placeholder.svg"
          alt="Destinations"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />
        <div className="absolute inset-0 flex items-center justify-center text-white">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2">Explore Destinations</h1>
            <p className="text-lg">Discover amazing places across Nigeria</p>
          </div>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-3">
          <nav className="text-sm text-gray-600">
            <a href="/" className="hover:text-blue-600">Home</a>
            <span className="mx-2">/</span>
            <span className="text-gray-900">Destinations</span>
          </nav>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Search */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search destinations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Destinations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredStates.map((state: any) => (
            <Card
              key={state.id}
              className="relative overflow-hidden cursor-pointer group shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105"
              onClick={() => handleStateClick(state.slug)}
            >
              <div className="relative h-48">
                <img
                  src={state.featured_image_url || '/placeholder.svg'}
                  alt={state.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/30 group-hover:from-black/70 group-hover:to-black/50 transition-all duration-300" />
                <div className="absolute top-4 left-4">
                  <div className="flex items-center gap-2">
                    <h3 className="text-2xl font-bold text-white">{state.name}</h3>
                    <span className="text-xl">🇳🇬</span>
                  </div>
                  <p className="text-white/90 text-lg mt-1">{state.hotel_count} hotels</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {filteredStates.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <p className="text-gray-600">No destinations found matching your search.</p>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default Destinations;