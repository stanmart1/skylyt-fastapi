import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Star, MapPin, ArrowLeft, Clock, Users, Wifi, Car, Coffee, Dumbbell, Waves, UtensilsCrossed, Building, Sparkles, ParkingCircle, Heart } from 'lucide-react';
import { apiService } from '@/services/api';
import Navigation from '@/components/Navigation';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface HotelDetail {
  id: string;
  name: string;
  location: string;
  star_rating: number;
  price_per_night: number;
  currency?: string;
  description: string;
  images: string[];
  amenities: string[];
  room_count: number;
  is_available: boolean;
  check_in_time: string;
  check_out_time: string;
  policies: string[];
}

const HotelDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currency } = useCurrency();
  const [hotel, setHotel] = useState<HotelDetail | null>(null);
  const [hotelImages, setHotelImages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const getAmenityIcon = (amenity: string) => {
    const amenityLower = amenity.toLowerCase();
    if (amenityLower.includes('wifi') || amenityLower.includes('internet')) return <Wifi className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('pool') || amenityLower.includes('swimming')) return <Waves className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('gym') || amenityLower.includes('fitness')) return <Dumbbell className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('restaurant') || amenityLower.includes('dining')) return <UtensilsCrossed className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('spa') || amenityLower.includes('wellness')) return <Sparkles className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('parking') || amenityLower.includes('valet')) return <ParkingCircle className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('business') || amenityLower.includes('conference')) return <Building className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('bar') || amenityLower.includes('lounge')) return <Coffee className="h-5 w-5 text-blue-600" />;
    if (amenityLower.includes('concierge') || amenityLower.includes('service')) return <Heart className="h-5 w-5 text-blue-600" />;
    return <Star className="h-5 w-5 text-blue-600" />;
  };

  useEffect(() => {
    const fetchHotelDetails = async () => {
      if (!id) {
        setError('Hotel ID is required');
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        setError(null);
        const data = await apiService.request(`/hotels/${id}?currency=${currency}`);
        
        if (!data || !data.id) {
          throw new Error('Invalid hotel data received');
        }
        
        setHotel(data);
        
        // Fetch hotel images
        try {
          const imagesData = await apiService.request(`/hotel-images/${id}`);
          setHotelImages(imagesData.images || []);
        } catch (imageErr) {
          console.error('Failed to fetch hotel images:', imageErr);
        }
      } catch (err: any) {
        console.error('Error fetching hotel details:', err);
        if (err.status === 404) {
          setError('Hotel not found');
        } else {
          setError('Failed to load hotel details. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchHotelDetails();
  }, [id, currency]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4" />
            <div className="h-64 bg-gray-200 rounded" />
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !hotel) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Hotel Not Found</h2>
            <p className="text-gray-600 mb-6">{error || 'The hotel you are looking for does not exist.'}</p>
            <Button onClick={() => navigate('/hotels')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Hotels
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <Button 
          onClick={() => navigate('/hotels')} 
          variant="outline" 
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Hotels
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Hotel Images Gallery */}
            <Card>
              <CardContent className="p-0">
                <div className="relative">
                  {/* Main Image */}
                  <img
                    src={hotelImages.length > 0 
                      ? (hotelImages[selectedImageIndex]?.image_url?.startsWith('http') 
                        ? hotelImages[selectedImageIndex].image_url 
                        : `https://skylytapi.scaleitpro.com${hotelImages[selectedImageIndex]?.image_url}`)
                      : (hotel.images && hotel.images.length > 0 ? hotel.images[0] : '/placeholder.svg')
                    }
                    alt={hotel.name}
                    className="w-full h-64 md:h-96 object-cover rounded-t-lg cursor-pointer"
                    onClick={() => {
                      // Simple lightbox - could be enhanced with a proper modal
                      const imageUrl = hotelImages.length > 0 
                        ? (hotelImages[selectedImageIndex]?.image_url?.startsWith('http') 
                          ? hotelImages[selectedImageIndex].image_url 
                          : `https://skylytapi.scaleitpro.com${hotelImages[selectedImageIndex]?.image_url}`)
                        : (hotel.images && hotel.images.length > 0 ? hotel.images[0] : '/placeholder.svg');
                      window.open(imageUrl, '_blank');
                    }}
                  />
                  {hotelImages.length > 1 && (
                    <div className="absolute bottom-4 right-4">
                      <Badge className="bg-black/70 text-white">
                        {selectedImageIndex + 1} of {hotelImages.length}
                      </Badge>
                    </div>
                  )}
                  {hotelImages.find(img => img.is_cover) && (
                    <div className="absolute top-4 left-4">
                      <Badge className="bg-yellow-500 text-white">
                        Cover Photo
                      </Badge>
                    </div>
                  )}
                </div>
                
                {/* Image Thumbnails */}
                {hotelImages.length > 1 && (
                  <div className="p-4">
                    <div className="flex gap-2 overflow-x-auto">
                      {hotelImages.map((image, index) => (
                        <img
                          key={image.id}
                          src={image.image_url?.startsWith('http') 
                            ? image.image_url 
                            : `https://skylytapi.scaleitpro.com${image.image_url}`}
                          alt={`${hotel.name} - Image ${index + 1}`}
                          className={`w-16 h-16 object-cover rounded cursor-pointer border-2 transition-all ${
                            selectedImageIndex === index 
                              ? 'border-blue-500 opacity-100' 
                              : 'border-gray-200 opacity-70 hover:opacity-100'
                          }`}
                          onClick={() => setSelectedImageIndex(index)}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Hotel Info */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl md:text-3xl">{hotel.name}</CardTitle>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-5 w-5 ${
                              i < hotel.star_rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                            }`}
                          />
                        ))}
                        <span className="ml-1 text-sm text-gray-600">({hotel.star_rating} stars)</span>
                      </div>
                    </div>
                    <div className="flex items-center text-gray-600 mt-2">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span>{hotel.location}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-blue-600">
                      <PriceDisplay amount={hotel.price_per_night} currency={hotel.currency || currency} />
                    </div>
                    <div className="text-sm text-gray-600">per night</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed">{hotel.description}</p>
              </CardContent>
            </Card>

            {/* Amenities */}
            <Card>
              <CardHeader>
                <CardTitle>Amenities</CardTitle>
              </CardHeader>
              <CardContent>
                {hotel.amenities && hotel.amenities.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {hotel.amenities.map((amenity) => (
                      <div key={amenity} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                        {getAmenityIcon(amenity)}
                        <span className="text-sm font-medium">{amenity}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No amenities listed</p>
                )}
              </CardContent>
            </Card>

            {/* Policies */}
            <Card>
              <CardHeader>
                <CardTitle>Hotel Policies</CardTitle>
              </CardHeader>
              <CardContent>
                {hotel.policies && hotel.policies.length > 0 ? (
                  <div className="space-y-2">
                    {hotel.policies.map((policy, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full mt-2" />
                        <span className="text-sm text-gray-700">{policy}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No policies listed</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Booking Card */}
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle>Book This Hotel</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span>Check-in: {hotel.check_in_time}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span>Check-out: {hotel.check_out_time}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-gray-500" />
                    <span>{hotel.room_count} rooms available</span>
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-lg font-semibold">Total per night</span>
                    <span className="text-2xl font-bold text-blue-600">
                      <PriceDisplay amount={hotel.price_per_night} currency={hotel.currency || currency} />
                    </span>
                  </div>
                  
                  <Button 
                    className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white font-semibold py-3 shadow-lg hover:shadow-xl transition-all duration-300"
                    onClick={() => {
                      if (hotel.is_available) {
                        window.location.href = `/booking?type=hotel&id=${hotel.id}`;
                      }
                    }}
                    disabled={!hotel.is_available}
                  >
                    {hotel.is_available ? 'Book Now' : 'Not Available'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HotelDetail;