import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Hotel, Plus, Edit, Trash2, ArrowLeft, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';

interface HotelData {
  id: string;
  name: string;
  location: string;
  rating: number;
  price: number;
  image_url?: string;
  amenities: string[];
  description: string;
  is_available: boolean;
  is_featured: boolean;
  room_count: number;
  features: string[];
}

const HotelManagement = () => {
  const [hotels, setHotels] = useState<HotelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHotel, setEditingHotel] = useState<HotelData | null>(null);
  const [hotelForm, setHotelForm] = useState({
    name: '',
    location: '',
    rating: 4,
    price: 0,
    image_url: '',
    amenities: '',
    description: ''
  });
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await apiService.request('/admin/hotels');
      console.log('HOTEL DATA RECEIVED:', data);
      console.log('FIRST HOTEL:', data[0]);
      setHotels(data);
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddHotel = () => {
    setEditingHotel(null);
    setHotelForm({
      name: '',
      location: '',
      rating: 4,
      price: 0,
      image_url: '',
      amenities: '',
      description: ''
    });
    setIsModalOpen(true);
  };

  const handleEditHotel = (hotel: HotelData) => {
    setEditingHotel(hotel);
    setHotelForm({
      name: hotel.name,
      location: hotel.location,
      rating: hotel.rating,
      price: hotel.price,
      image_url: hotel.image_url || '',
      amenities: hotel.amenities.join(', '),
      description: hotel.description
    });
    setIsModalOpen(true);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
formData.append('upload_type', 'general');

      const response = await apiService.uploadFile(formData);
      setHotelForm({...hotelForm, image_url: response.url});
    } catch (error) {
      console.error('Failed to upload image:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleSaveHotel = async () => {
    try {
      const hotelData = {
        ...hotelForm,
        amenities: hotelForm.amenities.split(',').map(a => a.trim()).filter(a => a)
      };

      console.log('Saving hotel data:', hotelData);

      if (editingHotel) {
        await apiService.request(`/admin/hotels/${editingHotel.id}`, {
          method: 'PUT',
          body: JSON.stringify(hotelData)
        });
      } else {
        await apiService.request('/admin/hotels', {
          method: 'POST',
          body: JSON.stringify(hotelData)
        });
      }

      await fetchHotels();
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to save hotel:', error);
    }
  };

  const handleToggleFeatured = async (hotelId: string, currentFeatured: boolean) => {
    try {
      await apiService.request(`/admin/hotels/${hotelId}/feature`, {
        method: 'POST'
      });
      await fetchHotels();
    } catch (error) {
      console.error('Failed to toggle featured status:', error);
    }
  };

  const handleDeleteHotel = async (hotelId: string) => {
    if (!confirm('Are you sure you want to delete this hotel?')) return;

    try {
      await apiService.request(`/admin/hotels/${hotelId}`, { method: 'DELETE' });
      await fetchHotels();
    } catch (error) {
      console.error('Failed to delete hotel:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={() => navigate('/admin')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Admin
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Hotel Management</h1>
              <p className="text-gray-600">Manage your hotel partners</p>
            </div>
          </div>
          <Button onClick={handleAddHotel}>
            <Plus className="h-4 w-4 mr-2" />
            Add Hotel
          </Button>
        </div>

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
                <CardContent className="p-0">
                  {hotel.image_url && (
                    <img 
                      src={(() => {
                        const url = apiService.getImageUrl(hotel.image_url || '');
                        console.log('Final image URL:', url);
                        return url;
                      })()} 
                      alt={hotel.name}
                      className="w-full h-48 object-cover rounded-t-lg"
                      onError={(e) => {
                        console.log('Image failed to load:', e.currentTarget.src);
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <Hotel className="h-8 w-8 text-blue-600" />
                      <Badge className={hotel.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {hotel.is_available ? 'Available' : 'Unavailable'}
                      </Badge>
                    </div>
                  <h3 className="font-semibold text-lg">{hotel.name}</h3>
                  <p className="text-gray-600 mb-2">{hotel.location}</p>
                  <div className="flex items-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star 
                        key={i} 
                        className={`h-4 w-4 ${i < hotel.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                      />
                    ))}
                    <span className="text-sm text-gray-600 ml-1">({hotel.rating})</span>
                  </div>
                  <p className="text-lg font-bold text-blue-600">${hotel.price}/night</p>
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">{hotel.description}</p>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" onClick={() => handleEditHotel(hotel)}>
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => alert('Featured button works!')}
                      className="bg-yellow-100 text-yellow-800"
                    >
                      <Star className="h-3 w-3 fill-current" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleDeleteHotel(hotel.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Add/Edit Hotel Modal */}
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{editingHotel ? 'Edit Hotel' : 'Add New Hotel'}</DialogTitle>
              <DialogDescription>
                {editingHotel ? 'Update hotel information and settings' : 'Add a new hotel to your platform'}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Hotel Name</Label>
                <Input
                  id="name"
                  value={hotelForm.name}
                  onChange={(e) => setHotelForm({...hotelForm, name: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={hotelForm.location}
                  onChange={(e) => setHotelForm({...hotelForm, location: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="rating">Rating (1-5)</Label>
                  <Input
                    id="rating"
                    type="number"
                    min="1"
                    max="5"
                    value={hotelForm.rating}
                    onChange={(e) => setHotelForm({...hotelForm, rating: Number(e.target.value)})}
                  />
                </div>
                <div>
                  <Label htmlFor="price">Price per night</Label>
                  <Input
                    id="price"
                    type="number"
                    value={hotelForm.price}
                    onChange={(e) => setHotelForm({...hotelForm, price: Number(e.target.value)})}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="amenities">Amenities (comma separated)</Label>
                <Input
                  id="amenities"
                  value={hotelForm.amenities}
                  onChange={(e) => setHotelForm({...hotelForm, amenities: e.target.value})}
                  placeholder="WiFi, Pool, Gym, Spa"
                />
              </div>
              <div>
                <Label htmlFor="image">Hotel Image</Label>
                <Input
                  id="image"
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
                {uploading && <p className="text-sm text-gray-500 mt-1">Uploading...</p>}
                {hotelForm.image_url && (
                  <img 
                    src={apiService.getImageUrl(hotelForm.image_url || '')} 
                    alt="Preview" 
                    className="mt-2 w-20 h-20 object-cover rounded"
                  />
                )}
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={hotelForm.description}
                  onChange={(e) => setHotelForm({...hotelForm, description: e.target.value})}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button onClick={handleSaveHotel}>
                  {editingHotel ? 'Update Hotel' : 'Add Hotel'}
                </Button>
                <Button variant="outline" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default HotelManagement;