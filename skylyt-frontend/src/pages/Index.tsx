
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Car, Hotel, MapPin, Calendar, Users, Star, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navigation from '@/components/Navigation';
import FeaturedCars from '@/components/FeaturedCars';
import FeaturedHotels from '@/components/FeaturedHotels';
import TrendingDestinations from '@/components/destinations/TrendingDestinations';
import Footer from '@/components/Footer';
import '../styles/hero-animations.css';

const Index = () => {
  const [searchType, setSearchType] = useState('cars');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-600 via-blue-700 to-teal-600 text-white py-36 overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        {/* Floating particles */}
        <div className="absolute inset-0">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
        </div>
        <div className="relative container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4 hero-title">
              Your Perfect Journey Awaits
            </h1>
            <p className="text-xl opacity-90 max-w-2xl mx-auto hero-subtitle">
              Discover amazing cars and luxurious hotels for your next adventure. 
              Book with confidence and travel in style.
            </p>
          </div>

          {/* Search Section */}
          <div className="max-w-4xl mx-auto">
            <Tabs value={searchType} onValueChange={setSearchType} className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6 bg-white/20 backdrop-blur-sm tab-list">
                <TabsTrigger value="cars" className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=inactive]:text-white/90 data-[state=inactive]:hover:text-white tab-trigger">
                  <Car className="h-4 w-4 tab-icon" />
                  Rent a Car
                </TabsTrigger>
                <TabsTrigger value="hotels" className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=inactive]:text-white/90 data-[state=inactive]:hover:text-white tab-trigger">
                  <Hotel className="h-4 w-4 tab-icon" />
                  Book a Hotel
                </TabsTrigger>
              </TabsList>

              <TabsContent value="cars">
                <Card className="bg-white/95 backdrop-blur-sm border-0 shadow-2xl">
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-blue-600" />
                        <Input placeholder="Pick-up location" className="border-0 bg-gray-50" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <Input type="date" className="border-0 bg-gray-50" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <Input type="date" className="border-0 bg-gray-50" />
                      </div>
                      <Button className="bg-orange-500 hover:bg-orange-600 text-white search-button">
                        <Search className="h-4 w-4 mr-2 search-icon" />
                        Search Cars
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="hotels">
                <Card className="bg-white/95 backdrop-blur-sm border-0 shadow-2xl">
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-blue-600" />
                        <Input placeholder="Destination" className="border-0 bg-gray-50" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <Input type="date" placeholder="Check-in" className="border-0 bg-gray-50" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <Input type="date" placeholder="Check-out" className="border-0 bg-gray-50" />
                      </div>
                      <Button className="bg-orange-500 hover:bg-orange-600 text-white search-button">
                        <Search className="h-4 w-4 mr-2 search-icon" />
                        Search Hotels
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </section>

      {/* Featured Cars Section */}
      <FeaturedCars />

      {/* Featured Hotels Section */}
      <FeaturedHotels />

      {/* Trending Destinations Section */}
      <TrendingDestinations />

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose Skylyt Luxury?</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              We provide the best booking experience with unmatched service quality
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            <Card className="text-center py-16 px-6 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-0 bg-white group">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Car className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Premium Vehicles</h3>
                <p className="text-gray-600">Choose from our extensive fleet of well-maintained, premium vehicles</p>
              </CardContent>
            </Card>
            
            <Card className="text-center py-16 px-6 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-0 bg-white group">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Hotel className="h-8 w-8 text-orange-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Luxury Hotels</h3>
                <p className="text-gray-600">Stay in handpicked hotels with exceptional service and amenities</p>
              </CardContent>
            </Card>
            
            <Card className="text-center py-16 px-6 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-0 bg-white group">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Star className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">24/7 Support</h3>
                <p className="text-gray-600">Round-the-clock customer support for a seamless experience</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
