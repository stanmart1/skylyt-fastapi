import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Users, Car, Fuel, Settings, Star, MapPin } from 'lucide-react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { apiService } from '@/services/api';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface CarDetails {
  id: string;
  name: string;
  category: string;
  price: number;
  currency?: string;
  passengers: number;
  transmission: string;
  fuel_type?: string;
  year?: number;
  brand?: string;
  model?: string;
  description?: string;
  features?: string[];
  image_url?: string;
  location?: string;
  rating?: number;
  available: boolean;
}

const CarDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currency } = useCurrency();
  const [car, setCar] = useState<CarDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchCarDetails(id);
    } else {
      setError('Invalid car ID');
      setLoading(false);
    }
  }, [id, currency]);

  const fetchCarDetails = async (carId: string) => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching car details for ID:', carId);
      const response = await apiService.request(`/cars/${carId}?currency=${currency}`);
      setCar(response);
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to load car details';
      setError(errorMessage);
      console.error('Error fetching car details for ID:', carId, 'Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-32 mb-6" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="h-96 bg-gray-200 rounded-lg" />
              <div className="space-y-4">
                <div className="h-8 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
                <div className="h-20 bg-gray-200 rounded" />
                <div className="h-12 bg-gray-200 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !car) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="text-center py-12">
            <Car className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Car not found</h3>
            <p className="text-gray-600">The car you're looking for doesn't exist or has been removed.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cars
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Car Image */}
          <div className="relative">
            {car.image_url ? (
              <img
                src={car.image_url}
                alt={car.name}
                className="w-full h-96 object-cover rounded-lg shadow-lg"
              />
            ) : (
              <div className="w-full h-96 bg-gray-200 rounded-lg shadow-lg flex items-center justify-center">
                <Car className="h-16 w-16 text-gray-400" />
              </div>
            )}
            <div className="absolute top-4 left-4">
              <Badge className="bg-blue-600 text-white">
                {car.category}
              </Badge>
            </div>
            {!car.available && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                <Badge variant="destructive" className="text-lg px-4 py-2">
                  Not Available
                </Badge>
              </div>
            )}
          </div>

          {/* Car Details */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{car.name}</h1>
              {car.location && (
                <div className="flex items-center text-gray-600 mb-2">
                  <MapPin className="h-4 w-4 mr-1" />
                  <span>{car.location}</span>
                </div>
              )}
              {car.rating && (
                <div className="flex items-center mb-4">
                  <Star className="h-4 w-4 text-yellow-500 fill-current mr-1" />
                  <span className="font-medium">{car.rating}</span>
                  <span className="text-gray-600 ml-1">rating</span>
                </div>
              )}
            </div>

            {car.description && (
              <p className="text-gray-600 leading-relaxed">{car.description}</p>
            )}

            {/* Car Specifications */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center text-gray-600">
                <Users className="h-5 w-5 mr-2" />
                <span>{car.passengers} passengers</span>
              </div>
              <div className="flex items-center text-gray-600">
                <Settings className="h-5 w-5 mr-2" />
                <span>{car.transmission}</span>
              </div>
              {car.fuel_type && (
                <div className="flex items-center text-gray-600">
                  <Fuel className="h-5 w-5 mr-2" />
                  <span>{car.fuel_type}</span>
                </div>
              )}
              {car.year && (
                <div className="flex items-center text-gray-600">
                  <Car className="h-5 w-5 mr-2" />
                  <span>{car.year}</span>
                </div>
              )}
            </div>

            {/* Price and Booking */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-3xl font-bold text-blue-600">
                    <PriceDisplay amount={car.price_per_day || car.price} currency={car.currency || currency} />
                  </span>
                  <span className="text-gray-600 ml-2">/day</span>
                </div>
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white"
                onClick={() => window.location.href = `/booking?type=car&id=${car.id}`}
                disabled={!car.available}
              >
                {car.available ? 'Book Now' : 'Not Available'}
              </Button>
            </div>
          </div>
        </div>

        {/* Features */}
        {car.features && car.features.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Features & Amenities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {car.features.map((feature, index) => (
                  <div key={index} className="flex items-center text-gray-600">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mr-3" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Additional Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Vehicle Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {car.brand && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Brand:</span>
                  <span className="font-medium">{car.brand}</span>
                </div>
              )}
              {car.model && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Model:</span>
                  <span className="font-medium">{car.model}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Category:</span>
                <span className="font-medium">{car.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Passengers:</span>
                <span className="font-medium">{car.passengers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Transmission:</span>
                <span className="font-medium">{car.transmission}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rental Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Daily Rate:</span>
                <span className="font-medium">
                  <PriceDisplay amount={car.price_per_day || car.price} currency={car.currency || currency} />/day
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Availability:</span>
                <Badge variant={car.available ? "default" : "destructive"}>
                  {car.available ? "Available" : "Not Available"}
                </Badge>
              </div>
              {car.location && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Location:</span>
                  <span className="font-medium">{car.location}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default CarDetail;