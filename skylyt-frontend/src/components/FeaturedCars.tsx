
import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Star, Users, Car, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { apiService } from '@/services/api';
import { Car as CarType } from '@/types/api';
import { useCurrencySearch } from '@/hooks/useCurrencySearch';
import PriceDisplay from './PriceDisplay';

const FeaturedCars = () => {
  const [cars, setCars] = useState<CarType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [cardsPerView, setCardsPerView] = useState(1);
  const { getFeaturedCars, refreshTrigger } = useCurrencySearch();

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
    const fetchFeaturedCars = async () => {
      try {
        const data = await getFeaturedCars();
        setCars(data.cars || []);
      } catch (error) {
        console.error('Failed to fetch featured cars:', error);
        setCars([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeaturedCars();
  }, [refreshTrigger]);
  
  const maxIndex = Math.max(0, cars.length - cardsPerView);
  
  const nextSlide = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, maxIndex));
  };
  
  const prevSlide = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  if (isLoading) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Cars</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Choose from our premium collection of vehicles for your perfect journey
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

  if (!cars || cars.length === 0) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Cars</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              No cars available at the moment
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Featured Cars</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Choose from our premium collection of vehicles for your perfect journey
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
              {cars && cars.map((car) => (
                <div key={car.id} className="w-full md:w-1/2 lg:w-1/3 flex-shrink-0 px-2">
                  <Card 
                    className="group hover:shadow-2xl transition-all duration-300 hover:scale-105 bg-white border-0 cursor-pointer"
                    onClick={() => {
                      if (car.id) {
                        window.location.href = `/car/${car.id}`;
                      }
                    }}
                  >
                    <CardContent className="p-0">
                      <div className="relative overflow-hidden rounded-t-lg">
                        <img
                          src={car.image_url}
                          alt={car.name}
                          className="w-full h-48 md:h-56 object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                        {/* Desktop Eye Icon - Centered */}
                        <div
                          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden lg:flex rounded-full w-14 h-14 shadow-lg items-center justify-center cursor-pointer z-20"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
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
                          <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                            {car.category}
                          </span>
                        </div>
                      </div>

                      <div className="p-4 md:p-6">
                        <h3 className="text-lg md:text-xl font-semibold mb-3">{car.name}</h3>

                        <div className="flex items-center text-gray-600 text-sm mb-4">
                          <Users className="h-4 w-4 mr-1" />
                          <span className="mr-4">{car.passengers} seats</span>
                          <Car className="h-4 w-4 mr-1" />
                          <span>{car.transmission}</span>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <PriceDisplay 
                              amount={car.price} 
                              currency={car.currency}
                              className="text-2xl md:text-3xl font-bold text-blue-600"
                            />
                            <span className="text-gray-600 text-sm">/day</span>
                          </div>
                          <Button 
                            className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 text-sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              window.location.href = `/booking?type=car&id=${car.id}`;
                            }}
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
                  index === currentIndex ? 'bg-blue-600' : 'bg-gray-300'
                }`}
                onClick={() => setCurrentIndex(index)}
              />
            ))}
          </div>
        </div>

        <div className="text-center mt-8">
          <Button 
            variant="outline" 
            className="border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white"
            onClick={() => window.location.href = '/cars'}
          >
            View All Cars
          </Button>
        </div>
      </div>
    </section>
  );
};

export default FeaturedCars;
