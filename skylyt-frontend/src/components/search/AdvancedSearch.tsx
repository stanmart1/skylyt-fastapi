import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { MapPin, Calendar, Users, Search, Filter } from 'lucide-react';
import { SearchParams } from '@/types/api';

interface AdvancedSearchProps {
  onSearch: (params: SearchParams) => void;
  type: 'hotel' | 'car';
}

export const AdvancedSearch = ({ onSearch, type }: AdvancedSearchProps) => {
  const [searchParams, setSearchParams] = useState<SearchParams>({
    destination: '',
    check_in: '',
    check_out: '',
    guests: 1,
    min_price: 0,
    max_price: 1000,
    amenities: [],
    rating: 0,
    sort_by: 'price',
    page: 1,
    per_page: 20,
  });

  const [showFilters, setShowFilters] = useState(false);

  const handleInputChange = (field: keyof SearchParams, value: any) => {
    setSearchParams(prev => ({ ...prev, [field]: value }));
  };

  const handleAmenityChange = (amenity: string, checked: boolean) => {
    setSearchParams(prev => ({
      ...prev,
      amenities: checked
        ? [...(prev.amenities || []), amenity]
        : (prev.amenities || []).filter(a => a !== amenity)
    }));
  };

  const handleSearch = () => {
    onSearch(searchParams);
  };

  const amenitiesList = type === 'hotel' 
    ? ['WiFi', 'Pool', 'Gym', 'Spa', 'Restaurant', 'Parking', 'Pet Friendly', 'Business Center']
    : ['GPS', 'Bluetooth', 'AC', 'USB', 'Leather Seats', 'Sunroof', 'Premium Audio', 'Child Seat'];

  return (
    <Card className="bg-white shadow-sm">
      <CardContent className="p-4 space-y-4">
        <div className="border-b pb-3">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Filter className="h-5 w-5 text-blue-600" />
            Search Filters
          </h3>
        </div>

        {/* Destination */}
        <div className="space-y-2">
          <Label className="text-sm font-medium flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gray-500" />
            {type === 'hotel' ? 'Destination' : 'Pickup Location'}
          </Label>
          <Input
            placeholder={type === 'hotel' ? 'Enter city or hotel name' : 'Enter pickup location'}
            value={searchParams.destination}
            onChange={(e) => handleInputChange('destination', e.target.value)}
            className="w-full"
          />
        </div>

        {/* Dates */}
        <div className="space-y-3">
          <div className="space-y-2">
            <Label className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              Check-in
            </Label>
            <Input
              type="date"
              value={searchParams.check_in}
              onChange={(e) => handleInputChange('check_in', e.target.value)}
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <Label className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              Check-out
            </Label>
            <Input
              type="date"
              value={searchParams.check_out}
              onChange={(e) => handleInputChange('check_out', e.target.value)}
              className="w-full"
            />
          </div>
        </div>

        {/* Guests */}
        <div className="space-y-2">
          <Label className="text-sm font-medium flex items-center gap-2">
            <Users className="h-4 w-4 text-gray-500" />
            Guests
          </Label>
          <Select value={String(searchParams.guests)} onValueChange={(value) => handleInputChange('guests', Number(value))}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select guests" />
            </SelectTrigger>
            <SelectContent>
              {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                <SelectItem key={num} value={String(num)}>{num} Guest{num > 1 ? 's' : ''}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Price Range */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Price Range</Label>
          <div className="text-xs text-gray-600 mb-2">
            ${searchParams.min_price} - ${searchParams.max_price}
          </div>
          <Slider
            value={[searchParams.min_price || 0, searchParams.max_price || 1000]}
            onValueChange={([min, max]) => {
              handleInputChange('min_price', min);
              handleInputChange('max_price', max);
            }}
            max={1000}
            step={10}
            className="w-full"
          />
        </div>

        {/* Rating */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Minimum Rating</Label>
          <Select value={String(searchParams.rating)} onValueChange={(value) => handleInputChange('rating', Number(value))}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Any Rating" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0">Any Rating</SelectItem>
              <SelectItem value="3">3+ Stars</SelectItem>
              <SelectItem value="4">4+ Stars</SelectItem>
              <SelectItem value="5">5 Stars</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sort By */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Sort By</Label>
          <Select value={searchParams.sort_by} onValueChange={(value) => handleInputChange('sort_by', value)}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="price">Price (Low to High)</SelectItem>
              <SelectItem value="-price">Price (High to Low)</SelectItem>
              <SelectItem value="rating">Rating</SelectItem>
              <SelectItem value="name">Name</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Amenities/Features */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">{type === 'hotel' ? 'Amenities' : 'Features'}</Label>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {amenitiesList.map(amenity => (
              <div key={amenity} className="flex items-center space-x-2">
                <Checkbox
                  id={amenity}
                  checked={(searchParams.amenities || []).includes(amenity)}
                  onCheckedChange={(checked) => handleAmenityChange(amenity, !!checked)}
                />
                <Label htmlFor={amenity} className="text-sm cursor-pointer">{amenity}</Label>
              </div>
            ))}
          </div>
        </div>

        {/* Search Button */}
        <Button onClick={handleSearch} className="w-full bg-blue-600 hover:bg-blue-700">
          <Search className="h-4 w-4 mr-2" />
          Search {type === 'hotel' ? 'Hotels' : 'Cars'}
        </Button>
      </CardContent>
    </Card>
  );
};