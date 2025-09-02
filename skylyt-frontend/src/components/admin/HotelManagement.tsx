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
import { Plus, Edit, Trash2, Star, Hotel, Calendar, Users, DollarSign, Bed, MapPin, Wifi, Car as CarIcon, Coffee, Utensils, Dumbbell, Waves, Shield, CheckCircle } from 'lucide-react';
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

export const HotelManagement: React.FC = () => {
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
      setStats({
        total_hotels: data.totalHotels || 0,
        total_rooms: data.totalRooms || 0,
        occupied_rooms: data.activeBookings || 0,
        average_occupancy: data.occupancyRate || 0,
        revenue_today: data.totalRevenue || 0,
        average_rating: 4.5 // Default rating since not provided by API
      });
    } catch (error) {
      console.error('Failed to fetch hotel stats:', error);
      // Fallback to default values
      setStats({
        total_hotels: 0,
        total_rooms: 0,
        occupied_rooms: 0,
        average_occupancy: 0,
        revenue_today: 0,
        average_rating: 0
      });
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

  const handleEditHotel = (hotel: any) => {
    setEditingHotel(hotel);
    setHotelForm({
      name: hotel.name || '',
      location: hotel.location || '',
      city: hotel.city || '',
      state: hotel.state || '',
      country: hotel.country || '',
      star_rating: hotel.star_rating || hotel.rating || 5,
      price_per_night: hotel.price_per_night || hotel.price || 0,
      room_count: hotel.room_count || 1,
      description: hotel.description || '',
      amenities: Array.isArray(hotel.amenities) ? hotel.amenities.join(', ') : '',
      features: Array.isArray(hotel.features) ? hotel.features.join(', ') : '',
      contact_email: hotel.contact_email || '',
      contact_phone: hotel.contact_phone || '',
      check_in_time: hotel.check_in_time || '15:00',
      check_out_time: hotel.check_out_time || '11:00',
      cancellation_policy: hotel.cancellation_policy || '',
      is_available: hotel.is_available !== undefined ? hotel.is_available : true
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
      
      // Upload images if selected
      if (hotelImageFiles.length > 0) {
        const imageUrls = await handleHotelImagesUpload(hotelImageFiles);
        if (imageUrls.length > 0) {
          finalHotelData.image_url = imageUrls[0]; // Set primary image
          finalHotelData.images = imageUrls; // Set all images
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

  const handleFeatureHotel = async (hotelId: string) => {
    try {
      await apiService.request(`/admin/hotels/${hotelId}/feature`, { method: 'POST' });
      await fetchHotels();
      await fetchStats();
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
      await fetchStats();
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

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex justify-end">
        {hasPermission('content.manage_hotels') && (
          <Button onClick={handleAddHotel} className="w-full sm:w-auto">
            <Plus className="h-4 w-4 mr-2" />
            Add Hotel
          </Button>
        )}
      </div>

      {/* Hotel Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Total Hotels</p>
                <p className="text-xl sm:text-2xl font-bold">{loading ? '...' : (stats.total_hotels || 0)}</p>
              </div>
              <Hotel className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Total Rooms</p>
                <p className="text-xl sm:text-2xl font-bold text-green-600">{loading ? '...' : (stats.total_rooms || 0)}</p>
              </div>
              <Bed className="h-6 w-6 sm:h-8 sm:w-8 text-green-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Occupied</p>
                <p className="text-xl sm:text-2xl font-bold text-blue-600">{loading ? '...' : (stats.occupied_rooms || 0)}</p>
              </div>
              <Users className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Occupancy</p>
                <p className="text-xl sm:text-2xl font-bold text-yellow-600">{loading ? '...' : (stats.average_occupancy || 0)}%</p>
              </div>
              <CheckCircle className="h-6 w-6 sm:h-8 sm:w-8 text-yellow-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Revenue</p>
                <p className="text-lg sm:text-2xl font-bold text-green-600">
                  {loading ? '...' : <PriceDisplay amount={stats.revenue_today || 0} currency={currency} />}
                </p>
              </div>
              <DollarSign className="h-6 w-6 sm:h-8 sm:w-8 text-green-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Avg Rating</p>
                <p className="text-xl sm:text-2xl font-bold text-purple-600">{loading ? '...' : (stats.average_rating || 0)}</p>
              </div>
              <Star className="h-6 w-6 sm:h-8 sm:w-8 text-purple-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4 sm:p-6">
                <div className="h-32 bg-gray-200 rounded mb-4" />
                <div className="h-4 bg-gray-200 rounded mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : hotels.length === 0 ? (
        <Card>
          <CardContent className="p-8 sm:p-12 text-center">
            <Hotel className="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">No hotels found</h3>
            <p className="text-sm sm:text-base text-gray-600 mb-6">Get started by adding your first hotel property to the system.</p>
            {hasPermission('content.manage_hotels') && (
              <Button onClick={handleAddHotel}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Hotel
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {hotels.map((hotel) => (
            <Card key={hotel.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4 sm:p-6">
                {hotel.image_url ? (
                  <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                    <img src={hotel.image_url} alt={hotel.name} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                    <Hotel className="h-8 w-8 text-gray-400" />
                  </div>
                )}
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-base sm:text-lg truncate pr-2">{hotel.name}</h3>
                  {hotel.is_featured && (
                    <Badge className="bg-yellow-100 text-yellow-800 flex-shrink-0 text-xs">
                      <Star className="h-3 w-3 mr-1 fill-current" />
                      Featured
                    </Badge>
                  )}
                </div>
                <p className="text-gray-600 mb-2 text-sm truncate">{hotel.location}</p>
                <div className="flex items-center gap-1 mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`h-3 w-3 sm:h-4 sm:w-4 ${i < (hotel.star_rating || hotel.rating || 0) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                  ))}
                  <span className="text-xs sm:text-sm text-gray-600 ml-1">({hotel.star_rating || hotel.rating || 0})</span>
                </div>
                <p className="text-base sm:text-lg font-bold text-blue-600 mb-3">
                  <PriceDisplay amount={hotel.price_per_night || hotel.price || 0} currency={hotel.currency || currency} />/night
                </p>
                <p className="text-xs sm:text-sm text-gray-600 mb-4 line-clamp-2">{hotel.description}</p>
                <div className="flex flex-wrap gap-2">
                  {hasPermission('content.manage_hotels') && (
                    <Button variant="outline" size="sm" onClick={() => handleEditHotel(hotel)} className="flex-1 sm:flex-none">
                      <Edit className="h-3 w-3 sm:mr-1" />
                      <span className="hidden sm:inline">Edit</span>
                    </Button>
                  )}
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleFeatureHotel(hotel.id)}
                    className={`${hotel.is_featured ? 'bg-yellow-100 text-yellow-800' : 'text-gray-600 hover:text-gray-700'} flex-1 sm:flex-none`}
                    title={hotel.is_featured ? 'Remove from featured' : 'Add to featured'}
                  >
                    <Star className={`h-3 w-3 ${hotel.is_featured ? 'fill-current' : ''} sm:mr-1`} />
                    <span className="hidden sm:inline">{hotel.is_featured ? 'Featured' : 'Feature'}</span>
                  </Button>
                  {hasPermission('content.manage_hotels') && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setDeleteConfirm({ open: true, hotelId: hotel.id, hotelName: hotel.name })}
                      className="text-red-600 hover:text-red-700 flex-1 sm:flex-none"
                    >
                      <Trash2 className="h-3 w-3 sm:mr-1" />
                      <span className="hidden sm:inline">Delete</span>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto mx-4" aria-describedby="hotel-dialog-description">
          <DialogHeader>
            <DialogTitle className="text-lg sm:text-xl">{editingHotel ? 'Edit Hotel' : 'Add New Hotel'}</DialogTitle>
            <DialogDescription id="hotel-dialog-description" className="text-sm sm:text-base">
              {editingHotel ? 'Update the hotel details below.' : 'Add a new hotel property to your portfolio.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-sm font-medium">Hotel Name</Label>
              <Input id="name" value={hotelForm.name} onChange={(e) => setHotelForm({...hotelForm, name: e.target.value})} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="location" className="text-sm font-medium">Location</Label>
              <Input id="location" value={hotelForm.location} onChange={(e) => setHotelForm({...hotelForm, location: e.target.value})} className="mt-1" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="star_rating" className="text-sm font-medium">Rating (1-5)</Label>
                <Input id="star_rating" type="number" min="1" max="5" value={hotelForm.star_rating} onChange={(e) => setHotelForm({...hotelForm, star_rating: Number(e.target.value)})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="price_per_night" className="text-sm font-medium">Price per night</Label>
                <Input id="price_per_night" type="number" value={hotelForm.price_per_night} onChange={(e) => setHotelForm({...hotelForm, price_per_night: Number(e.target.value)})} className="mt-1" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="city" className="text-sm font-medium">City</Label>
                <Input id="city" value={hotelForm.city} onChange={(e) => setHotelForm({...hotelForm, city: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="state" className="text-sm font-medium">State</Label>
                <Input id="state" value={hotelForm.state} onChange={(e) => setHotelForm({...hotelForm, state: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="country" className="text-sm font-medium">Country</Label>
                <Input id="country" value={hotelForm.country} onChange={(e) => setHotelForm({...hotelForm, country: e.target.value})} className="mt-1" />
              </div>
            </div>
            <div>
              <Label htmlFor="room_count" className="text-sm font-medium">Total Rooms</Label>
              <Input id="room_count" type="number" min="1" value={hotelForm.room_count} onChange={(e) => setHotelForm({...hotelForm, room_count: Number(e.target.value)})} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="hotel_images" className="text-sm font-medium">Hotel Images</Label>
              <div className="space-y-2 mt-1">
                <input
                  id="hotel_images"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => setHotelImageFiles(Array.from(e.target.files || []))}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('hotel_images')?.click()}
                  disabled={uploadingHotelImages}
                  className="w-full sm:w-auto"
                >
                  {uploadingHotelImages ? 'Uploading...' : 'Choose Images'}
                </Button>
                {hotelImageFiles.length > 0 && (
                  <div className="text-xs sm:text-sm text-gray-600 p-2 bg-gray-50 rounded">
                    {hotelImageFiles.length} image(s) selected: {hotelImageFiles.map(f => f.name).slice(0, 3).join(', ')}
                    {hotelImageFiles.length > 3 && ` and ${hotelImageFiles.length - 3} more...`}
                  </div>
                )}
              </div>
            </div>
            <div>
              <Label htmlFor="amenities" className="text-sm font-medium">Amenities (comma separated)</Label>
              <Input id="amenities" value={hotelForm.amenities} onChange={(e) => setHotelForm({...hotelForm, amenities: e.target.value})} placeholder="WiFi, Pool, Gym, Spa" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="features" className="text-sm font-medium">Features (comma separated)</Label>
              <Input id="features" value={hotelForm.features} onChange={(e) => setHotelForm({...hotelForm, features: e.target.value})} placeholder="Ocean View, Balcony, Kitchen" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="description" className="text-sm font-medium">Description</Label>
              <Textarea id="description" value={hotelForm.description} onChange={(e) => setHotelForm({...hotelForm, description: e.target.value})} placeholder="Hotel description..." rows={3} className="mt-1" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="contact_email" className="text-sm font-medium">Contact Email</Label>
                <Input id="contact_email" type="email" value={hotelForm.contact_email} onChange={(e) => setHotelForm({...hotelForm, contact_email: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="contact_phone" className="text-sm font-medium">Contact Phone</Label>
                <Input id="contact_phone" value={hotelForm.contact_phone} onChange={(e) => setHotelForm({...hotelForm, contact_phone: e.target.value})} className="mt-1" />
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-2 pt-4">
              <Button onClick={handleSaveHotel} className="w-full sm:w-auto" disabled={uploadingHotelImages}>
                {uploadingHotelImages ? 'Uploading...' : (editingHotel ? 'Update Hotel' : 'Add Hotel')}
              </Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)} className="w-full sm:w-auto">Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteConfirm.open}
        onOpenChange={(open) => setDeleteConfirm({ ...deleteConfirm, open })}
        title="Delete Hotel"
        description={`Are you sure you want to delete "${deleteConfirm.hotelName}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="destructive"
        onConfirm={handleDeleteHotel}
      />
    </div>
  );
};