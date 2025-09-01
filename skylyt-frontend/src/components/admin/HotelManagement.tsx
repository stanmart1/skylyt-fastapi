import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus, Edit, Trash2, Star, Hotel } from 'lucide-react';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';

export const HotelManagement: React.FC = () => {
  const { currency } = useCurrency();
  const { toast } = useToast();
  const [hotels, setHotels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHotel, setEditingHotel] = useState<any>(null);
  const [hotelForm, setHotelForm] = useState({
    name: '',
    location: '',
    rating: 4,
    price: 0,
    image_url: '',
    amenities: '',
    description: ''
  });
  const [hotelImageFiles, setHotelImageFiles] = useState<File[]>([]);
  const [uploadingHotelImages, setUploadingHotelImages] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; hotelId: string; hotelName: string }>({
    open: false,
    hotelId: '',
    hotelName: ''
  });

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await apiService.request('/admin/hotels');
      setHotels(data);
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

  const handleAddHotel = () => {
    setEditingHotel(null);
    setHotelForm({ name: '', location: '', rating: 4, price: 0, image_url: '', amenities: '', description: '' });
    setHotelImageFiles([]);
    setIsModalOpen(true);
  };

  const handleEditHotel = (hotel: any) => {
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
      let finalHotelData = { ...hotelForm, amenities: hotelForm.amenities.split(',').map(a => a.trim()).filter(a => a) };
      
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Hotel Management</h2>
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
              <CardContent className="p-6">
                {hotel.image_url ? (
                  <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                    <img src={hotel.image_url} alt={hotel.name} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                    <Hotel className="h-8 w-8 text-gray-400" />
                  </div>
                )}
                <h3 className="font-semibold text-lg">{hotel.name}</h3>
                <p className="text-gray-600 mb-2">{hotel.location}</p>
                <div className="flex items-center gap-1 mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`h-4 w-4 ${i < hotel.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                  ))}
                  <span className="text-sm text-gray-600 ml-1">({hotel.rating})</span>
                </div>
                <p className="text-lg font-bold text-blue-600">
                  <PriceDisplay amount={hotel.price} currency={hotel.currency || currency} />/night
                </p>
                <p className="text-sm text-gray-600 mt-2 line-clamp-2">{hotel.description}</p>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" onClick={() => handleEditHotel(hotel)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleFeatureHotel(hotel.id)}
                    className={hotel.is_featured ? 'bg-yellow-100 text-yellow-800' : ''}
                    title={hotel.is_featured ? 'Remove from featured' : 'Add to featured'}
                  >
                    <Star className={`h-3 w-3 ${hotel.is_featured ? 'fill-current' : ''}`} />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setDeleteConfirm({ open: true, hotelId: hotel.id, hotelName: hotel.name })}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingHotel ? 'Edit Hotel' : 'Add New Hotel'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Hotel Name</Label>
              <Input id="name" value={hotelForm.name} onChange={(e) => setHotelForm({...hotelForm, name: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Input id="location" value={hotelForm.location} onChange={(e) => setHotelForm({...hotelForm, location: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="rating">Rating (1-5)</Label>
                <Input id="rating" type="number" min="1" max="5" value={hotelForm.rating} onChange={(e) => setHotelForm({...hotelForm, rating: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="price">Price per night</Label>
                <Input id="price" type="number" value={hotelForm.price} onChange={(e) => setHotelForm({...hotelForm, price: Number(e.target.value)})} />
              </div>
            </div>
            <div>
              <Label htmlFor="hotel_images">Hotel Images</Label>
              <div className="space-y-2">
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
                >
                  {uploadingHotelImages ? 'Uploading...' : 'Choose Images'}
                </Button>
                {hotelImageFiles.length > 0 && (
                  <div className="text-sm text-gray-600">
                    {hotelImageFiles.length} image(s) selected: {hotelImageFiles.map(f => f.name).join(', ')}
                  </div>
                )}
              </div>
            </div>
            <div>
              <Label htmlFor="amenities">Amenities (comma separated)</Label>
              <Input id="amenities" value={hotelForm.amenities} onChange={(e) => setHotelForm({...hotelForm, amenities: e.target.value})} placeholder="WiFi, Pool, Gym, Spa" />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input id="description" value={hotelForm.description} onChange={(e) => setHotelForm({...hotelForm, description: e.target.value})} placeholder="Hotel description..." />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveHotel}>{editingHotel ? 'Update Hotel' : 'Add Hotel'}</Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
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