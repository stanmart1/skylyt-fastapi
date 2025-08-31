
import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Star, MapPin, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { apiService } from '@/services/api';
import { Hotel } from '@/types/api';
import { useCurrencySearch } from '@/hooks/useCurrencySearch';
import PriceDisplay from './PriceDisplay';

const FeaturedHotels = () => {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [cardsPerView, setCardsPerView] = useState(1);
  const { getFeaturedHotels, refreshTrigger } = useCurrencySearch();

  useEffect(() => {
    const updateCardsPerView = () => {
      if (window.innerWidth >= 1024) setCardsPerView(3);
      else if (window.innerWidth >= 768) setCardsPerView(2);
      else setCardsPerView(1);
    };
    
    updateCardsPerView();
    window.addEventListener('resize', updateCardsPerView);
    return () => window.removeEventListener('resize', updateCardsPerView);
  }, []);

  useEffect(() => {
    const fetchFeaturedHotels = async () => {
      try {
        const data = await getFeaturedHotels();
        setHotels(data.hotels || []);
      } catch (error) {
        console.error('Failed to fetch featured hotels:', error);
        setHotels([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeaturedHotels();
  }, [refreshTrigger]);
  
  const maxIndex = Math.max(0, hotels.length - cardsPerView);
  
  const nextSlide = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, maxIndex));
  };
  
  const prevSlide = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  if (isLoading) {
    return (
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Hotels</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Discover comfortable accommodations with exceptional service and amenities
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-48 bg-gray-200 rounded-t-lg" />
                <div className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4" />
                  <div className="flex justify-between">
                    <div className="h-6 bg-gray-200 rounded w-16" />
                    <div className="h-8 bg-gray-200 rounded w-20" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (hotels.length === 0) {
    return (
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Hotels</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              No hotels available at the moment
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Featured Hotels</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover comfortable accommodations with exceptional service and amenities
          </p>
        </div>

        <div className="relative max-w-6xl mx-auto">
          {/* Carousel Navigation */}
          <Button
            variant="outline"
            size="icon"
            className="absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white shadow-lg md:left-0"
            onClick={prevSlide}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <Button
            variant="outline"
            size="icon"
            className="absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white shadow-lg md:right-0"
            onClick={nextSlide}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          
          {/* Carousel Container */}
          <div className="overflow-hidden mx-8 md:mx-12">
            <div 
              className="flex transition-transform duration-500 ease-in-out"
              style={{ 
                transform: `translateX(-${currentIndex * (100 / cardsPerView)}%)` 
              }}
            >
              {hotels.map((hotel) => (
                <div key={hotel.id} className="w-full md:w-1/2 lg:w-1/3 flex-shrink-0 px-2">
                  <Card 
                    className="group hover:shadow-2xl transition-all duration-300 hover:scale-105 bg-white border-0 cursor-pointer lg:cursor-default"
                    onClick={() => {
                      if (window.innerWidth < 1024 && hotel.id) {
                        window.location.href = `/hotel/${hotel.id}`;
                      }
                    }}
                  >
                    <CardContent className="p-0">
                      <div className="relative overflow-hidden rounded-t-lg">
                        <img
                          src={hotel.image_url || '/placeholder.svg'}
                          alt={hotel.name}
                          className="w-full h-48 md:h-56 object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                        {/* Desktop Eye Icon - Centered */}
                        <div
                          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden lg:flex rounded-full w-14 h-14 shadow-lg items-center justify-center cursor-pointer z-20"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (hotel.id) {
                              window.location.href = `/hotel/${hotel.id}`;
                            }
                          }}
                        >
                          <Eye className="h-6 w-6 text-gray-900" />
                        </div>
                        {/* Overlay on hover */}
                        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 hidden lg:block" />
                        <div className="absolute top-4 left-4">
                          <span className="bg-teal-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                            {hotel.rating}★ Hotel
                          </span>
                        </div>
                      </div>

                      <div className="p-4 md:p-6">
                        <h3 className="text-lg md:text-xl font-semibold mb-3">{hotel.name}</h3>

                        <div className="flex items-center text-gray-600 text-sm mb-4">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span className="mr-4">{hotel.location}</span>
                          <Star className="h-4 w-4 mr-1 text-yellow-400 fill-current" />
                          <span>{hotel.rating}</span>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <PriceDisplay 
                              amount={hotel.price} 
                              currency={hotel.currency}
                              className="text-2xl md:text-3xl font-bold text-teal-600"
                            />
                            <span className="text-gray-600 text-sm">/night</span>
                          </div>
                          <Button 
                            className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 text-sm"
                            onClick={() => window.location.href = `/booking?type=hotel&id=${hotel.id}`}
                          >
                            Book Now
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </div>
          
          {/* Carousel Indicators */}
          <div className="flex justify-center mt-6 space-x-2">
            {Array.from({ length: maxIndex + 1 }).map((_, index) => (
              <button
                key={index}
                className={`w-3 h-3 rounded-full transition-colors duration-300 ${
                  index === currentIndex ? 'bg-teal-600' : 'bg-gray-300'
                }`}
                onClick={() => setCurrentIndex(index)}
              />
            ))}
          </div>
        </div>

        <div className="text-center mt-8">
          <Button 
            variant="outline" 
            className="border-teal-600 text-teal-600 hover:bg-teal-600 hover:text-white"
            onClick={() => window.location.href = '/hotels'}
          >
            View All Hotels
          </Button>
        </div>
      </div>
    </section>
  );
};

export default FeaturedHotels;
