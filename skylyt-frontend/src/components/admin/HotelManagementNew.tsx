import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Plus, Edit, Trash2, Star, Hotel, Calendar, Users, DollarSign, Bed, MapPin, Wifi, Car as CarIcon, Coffee, Utensils, Dumbbell, Waves, Shield, CheckCircle, Clock, AlertTriangle, Settings } from 'lucide-react';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

interface HotelData {
  id: string;
  name: string;
  location: string;
  city: string;
  state: string;
  country: string;
  star_rating: number;
  price_per_night: number;
  currency: string;
  room_count: number;
  available_rooms: number;
  images: string[];
  amenities: string[];
  description: string;
  features: string[];
  is_available: boolean;
  is_featured: boolean;
  contact_email: string;
  contact_phone: string;
  check_in_time: string;
  check_out_time: string;
  cancellation_policy: string;
  created_at: string;
  occupancy_rate: number;
  average_rating: number;
  total_reviews: number;
}

interface RoomType {
  id: string;
  hotel_id: string;
  name: string;
  type: string;
  capacity: number;
  price: number;
  available_count: number;
  total_count: number;
  amenities: string[];
  size_sqm: number;
  bed_type: string;
}

export const HotelManagementNew: React.FC = () => {
  const { currency } = useCurrency();
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [hotels, setHotels] = useState<HotelData[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('properties');
  const [stats, setStats] = useState({
    total_hotels: 0,
    total_rooms: 0,
    occupied_rooms: 0,
    average_occupancy: 0,
    revenue_today: 0,
    average_rating: 0
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHotel, setEditingHotel] = useState<HotelData | null>(null);
  const [hotelForm, setHotelForm] = useState({
    name: '',
    location: '',
    city: '',
    state: '',
    country: '',
    star_rating: 5,
    price_per_night: 0,
    room_count: 1,
    description: '',
    amenities: '',
    features: '',
    contact_email: '',
    contact_phone: '',
    check_in_time: '15:00',
    check_out_time: '11:00',
    cancellation_policy: '',
    is_available: true
  });
  const [roomForm, setRoomForm] = useState({
    hotel_id: '',
    name: '',
    type: '',
    capacity: 2,
    price: 0,
    total_count: 1,
    amenities: '',
    size_sqm: 25,
    bed_type: 'double'
  });
  const [isRoomModalOpen, setIsRoomModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<RoomType | null>(null);
  const [hotelImageFiles, setHotelImageFiles] = useState<File[]>([]);
  const [uploadingHotelImages, setUploadingHotelImages] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; hotelId: string; hotelName: string }>({
    open: false,
    hotelId: '',
    hotelName: ''
  });

  useEffect(() => {
    fetchHotels();
    fetchRoomTypes();
    fetchStats();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await apiService.request('/admin/hotels');
      setHotels(data || []);
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch hotels',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchRoomTypes = async () => {
    try {
      const data = await apiService.request('/admin/hotels/room-types');
      setRoomTypes(data || []);
    } catch (error) {
      console.error('Failed to fetch room types:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await apiService.request('/admin/hotels/stats');
      setStats(data || stats);
    } catch (error) {
      console.error('Failed to fetch hotel stats:', error);
    }
  };

  const handleAddHotel = () => {
    setEditingHotel(null);
    setHotelForm({
      name: '',
      location: '',
      city: '',
      state: '',
      country: '',
      star_rating: 5,
      price_per_night: 0,
      room_count: 1,
      description: '',
      amenities: '',
      features: '',
      contact_email: '',
      contact_phone: '',
      check_in_time: '15:00',
      check_out_time: '11:00',
      cancellation_policy: '',
      is_available: true
    });
    setHotelImageFiles([]);
    setIsModalOpen(true);
  };

  const handleEditHotel = (hotel: HotelData) => {
    setEditingHotel(hotel);
    setHotelForm({
      name: hotel.name,
      location: hotel.location,
      city: hotel.city || '',
      state: hotel.state || '',
      country: hotel.country || '',
      star_rating: hotel.star_rating,
      price_per_night: hotel.price_per_night,
      room_count: hotel.room_count,
      description: hotel.description,
      amenities: hotel.amenities?.join(', ') || '',
      features: hotel.features?.join(', ') || '',
      contact_email: hotel.contact_email || '',
      contact_phone: hotel.contact_phone || '',
      check_in_time: hotel.check_in_time || '15:00',
      check_out_time: hotel.check_out_time || '11:00',
      cancellation_policy: hotel.cancellation_policy || '',
      is_available: hotel.is_available
    });
    setHotelImageFiles([]);
    setIsModalOpen(true);
  };

  const handleHotelImagesUpload = async (files: File[]): Promise<string[]> => {
    setUploadingHotelImages(true);
    try {
      const uploadPromises = files.map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('upload_type', 'hotels');
        const response = await apiService.uploadFile(formData);
        return response.url;
      });
      
      const imageUrls = await Promise.all(uploadPromises);
      return imageUrls;
    } catch (error) {
      console.error('Failed to upload images:', error);
      toast({
        title: 'Error',
        description: 'Failed to upload images',
        variant: 'error'
      });
      return [];
    } finally {
      setUploadingHotelImages(false);
    }
  };

  const handleSaveHotel = async () => {
    try {
      let finalHotelData = { 
        ...hotelForm, 
        amenities: hotelForm.amenities.split(',').map(a => a.trim()).filter(a => a),
        features: hotelForm.features.split(',').map(f => f.trim()).filter(f => f)
      };
      
      if (hotelImageFiles.length > 0) {
        const imageUrls = await handleHotelImagesUpload(hotelImageFiles);
        if (imageUrls.length > 0) {
          finalHotelData.images = imageUrls;
        }
      }
      
      if (editingHotel) {
        await apiService.request(`/admin/hotels/${editingHotel.id}`, { method: 'PUT', body: JSON.stringify(finalHotelData) });
        toast({
          title: 'Success',
          description: 'Hotel updated successfully',
          variant: 'success'
        });
      } else {
        await apiService.request('/admin/hotels', { method: 'POST', body: JSON.stringify(finalHotelData) });
        toast({
          title: 'Success',
          description: 'Hotel added successfully',
          variant: 'success'
        });
      }
      await fetchHotels();
      await fetchStats();
      setIsModalOpen(false);
      setHotelImageFiles([]);
    } catch (error) {
      console.error('Failed to save hotel:', error);
      toast({
        title: 'Error',
        description: 'Failed to save hotel',
        variant: 'error'
      });
    }
  };

  const handleAddRoom = () => {
    setEditingRoom(null);
    setRoomForm({
      hotel_id: '',
      name: '',
      type: '',
      capacity: 2,
      price: 0,
      total_count: 1,
      amenities: '',
      size_sqm: 25,
      bed_type: 'double'
    });
    setIsRoomModalOpen(true);
  };

  const handleSaveRoom = async () => {
    try {
      const finalRoomData = {
        ...roomForm,
        amenities: roomForm.amenities.split(',').map(a => a.trim()).filter(a => a)
      };
      
      if (editingRoom) {
        await apiService.request(`/admin/hotels/room-types/${editingRoom.id}`, {
          method: 'PUT',
          body: JSON.stringify(finalRoomData)
        });
        toast({
          title: 'Success',
          description: 'Room type updated successfully',
          variant: 'success'
        });
      } else {
        await apiService.request('/admin/hotels/room-types', {
          method: 'POST',
          body: JSON.stringify(finalRoomData)
        });
        toast({
          title: 'Success',
          description: 'Room type added successfully',
          variant: 'success'
        });
      }
      await fetchRoomTypes();
      setIsRoomModalOpen(false);
    } catch (error) {
      console.error('Failed to save room type:', error);
      toast({
        title: 'Error',
        description: 'Failed to save room type',
        variant: 'error'
      });
    }
  };

  const handleFeatureHotel = async (hotelId: string) => {
    try {
      await apiService.request(`/admin/hotels/${hotelId}/feature`, { method: 'POST' });
      await fetchHotels();
      toast({
        title: 'Success',
        description: 'Hotel feature status updated',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to feature hotel:', error);
      toast({
        title: 'Error',
        description: 'Failed to update hotel feature status',
        variant: 'error'
      });
    }
  };

  const handleDeleteHotel = async () => {
    try {
      await apiService.request(`/admin/hotels/${deleteConfirm.hotelId}`, { method: 'DELETE' });
      await fetchHotels();
      toast({
        title: 'Success',
        description: 'Hotel deleted successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to delete hotel:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete hotel',
        variant: 'error'
      });
    }
  };

  const getAmenityIcon = (amenity: string) => {
    const amenityLower = amenity.toLowerCase();
    if (amenityLower.includes('wifi')) return <Wifi className="h-4 w-4" />;
    if (amenityLower.includes('parking')) return <CarIcon className="h-4 w-4" />;
    if (amenityLower.includes('breakfast')) return <Coffee className="h-4 w-4" />;
    if (amenityLower.includes('restaurant')) return <Utensils className="h-4 w-4" />;
    if (amenityLower.includes('gym')) return <Dumbbell className="h-4 w-4" />;
    if (amenityLower.includes('pool')) return <Waves className="h-4 w-4" />;
    if (amenityLower.includes('security')) return <Shield className="h-4 w-4" />;
    return <CheckCircle className="h-4 w-4" />;
  };

  const getOccupancyColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Hotel Management</h2>
          <p className="text-gray-600">Manage your hotel properties, rooms, and operations</p>
        </div>
        {hasPermission('content.manage_hotels') && (
          <Button onClick={handleAddHotel}>
            <Plus className="h-4 w-4 mr-2" />
            Add Hotel
          </Button>
        )}
      </div>

      {/* Hotel Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Hotels</p>
                <p className="text-2xl font-bold">{stats.total_hotels}</p>
              </div>
              <Hotel className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Rooms</p>
                <p className="text-2xl font-bold">{stats.total_rooms}</p>
              </div>
              <Bed className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Occupied</p>
                <p className="text-2xl font-bold text-blue-600">{stats.occupied_rooms}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Occupancy Rate</p>
                <p className={`text-2xl font-bold ${getOccupancyColor(stats.average_occupancy)}`}>
                  {stats.average_occupancy}%
                </p>
              </div>
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today's Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  <PriceDisplay amount={stats.revenue_today} currency={currency} />
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.average_rating}</p>
              </div>
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different sections */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="properties">Properties</TabsTrigger>
          <TabsTrigger value="rooms">Room Types</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="properties" className="space-y-4">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-32 bg-gray-200 rounded mb-4" />
                    <div className="h-4 bg-gray-200 rounded mb-2" />
                    <div className="h-4 bg-gray-200 rounded w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {hotels.map((hotel) => (
                <Card key={hotel.id}>
                  <CardContent className="p-6">
                    {hotel.images && hotel.images.length > 0 ? (
                      <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                        <img src={hotel.images[0]} alt={hotel.name} className="w-full h-full object-cover" />
                      </div>
                    ) : (
                      <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                        <Hotel className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-lg">{hotel.name}</h3>
                      <Badge variant={hotel.is_available ? 'default' : 'secondary'}>
                        {hotel.is_available ? 'Available' : 'Unavailable'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-1 mb-2">
                      <MapPin className="h-4 w-4 text-gray-500" />
                      <p className="text-gray-600 text-sm">{hotel.location}</p>
                    </div>
                    <div className="flex items-center mb-2">
                      {[...Array(hotel.star_rating)].map((_, i) => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                      ))}
                      <span className="ml-2 text-sm text-gray-600">({hotel.total_reviews} reviews)</span>
                    </div>
                    <p className="text-lg font-bold text-blue-600">
                      <PriceDisplay amount={hotel.price_per_night} currency={hotel.currency || currency} />/night
                    </p>
                    <div className="mt-4 space-y-1 text-sm text-gray-600">
                      <p>{hotel.room_count} rooms • {hotel.available_rooms} available</p>
                      <p className={`font-medium ${getOccupancyColor(hotel.occupancy_rate)}`}>
                        {hotel.occupancy_rate}% occupancy
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {hotel.amenities?.slice(0, 3).map((amenity, index) => (
                        <div key={index} className="flex items-center gap-1 text-xs text-gray-500">
                          {getAmenityIcon(amenity)}
                          <span>{amenity}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-2 mt-4">
                      {hasPermission('content.manage_hotels') && (
                        <Button variant="outline" size="sm" onClick={() => handleEditHotel(hotel)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleFeatureHotel(hotel.id)}
                        className={hotel.is_featured ? 'text-yellow-600 hover:text-yellow-700' : 'text-gray-600 hover:text-gray-700'}
                      >
                        <Star className={`h-3 w-3 ${hotel.is_featured ? 'fill-current' : ''}`} />
                      </Button>
                      {hasPermission('content.manage_hotels') && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setDeleteConfirm({ open: true, hotelId: hotel.id, hotelName: hotel.name })}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="rooms" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Room Types</h3>
            <Button onClick={handleAddRoom}>
              <Plus className="h-4 w-4 mr-2" />
              Add Room Type
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {roomTypes.map((room) => (
              <Card key={room.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{room.name}</h4>
                    <Badge>{room.type}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">Capacity: {room.capacity} guests</p>
                  <p className="text-sm text-gray-600 mb-2">Size: {room.size_sqm} m²</p>
                  <p className="text-lg font-bold text-blue-600 mb-2">
                    <PriceDisplay amount={room.price} currency={currency} />/night
                  </p>
                  <div className="flex justify-between text-sm text-gray-600 mb-4">
                    <span>Available: {room.available_count}</span>
                    <span>Total: {room.total_count}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {room.amenities?.slice(0, 3).map((amenity, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {amenity}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Occupancy Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total Rooms</span>
                    <span>{stats.total_rooms}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Occupied</span>
                    <span>{stats.occupied_rooms}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Occupancy</span>
                    <span className={getOccupancyColor(stats.average_occupancy)}>
                      {stats.average_occupancy}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Today's Revenue</span>
                    <span><PriceDisplay amount={stats.revenue_today} currency={currency} /></span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Rating</span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      {stats.average_rating}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>