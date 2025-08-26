import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, Link, Trash2, Star, StarOff, GripVertical } from 'lucide-react';
import { apiService } from '@/services/api';
import { sanitizeInput } from '@/utils/sanitize';

const HotelImageManagement = () => {
  const [hotels, setHotels] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState('');
  const [hotelImages, setHotelImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [draggedItem, setDraggedItem] = useState(null);

  useEffect(() => {
    fetchHotels();
  }, []);

  useEffect(() => {
    if (selectedHotel) {
      fetchHotelImages();
    }
  }, [selectedHotel]);

  const fetchHotels = async () => {
    try {
      const response = await apiService.request('/hotels');
      setHotels(response.hotels || []);
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
    }
  };

  const fetchHotelImages = async () => {
    if (!selectedHotel) return;
    
    setIsLoading(true);
    try {
      const response = await apiService.request(`/hotel-images/${selectedHotel}`);
      setHotelImages(response.images || []);
    } catch (error) {
      console.error('Failed to fetch hotel images:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (!selectedHotel || !files.length) return;

    const formData = new FormData();
    formData.append('hotel_id', selectedHotel);
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    setIsLoading(true);
    try {
      await apiService.uploadHotelImages(formData);
      fetchHotelImages();
    } catch (error) {
      console.error('Failed to upload images:', error);
      alert('Failed to upload images. Please check file size (max 5MB) and format (JPEG/PNG).');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlUpload = async () => {
    if (!selectedHotel || !imageUrl) return;

    const sanitizedUrl = sanitizeInput(imageUrl);
    if (!sanitizedUrl.startsWith('http')) {
      alert('Please enter a valid URL starting with http:// or https://');
      return;
    }

    const formData = new FormData();
    formData.append('hotel_id', selectedHotel);
    formData.append('image_url', sanitizedUrl);

    setIsLoading(true);
    try {
      await apiService.uploadHotelImageFromUrl(parseInt(selectedHotel), sanitizedUrl);
      setImageUrl('');
      fetchHotelImages();
    } catch (error) {
      console.error('Failed to upload image from URL:', error);
      alert('Failed to upload image from URL. Please check the URL and image format.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetCover = async (imageId: number) => {
    try {
      await apiService.setHotelImageAsCover(imageId);
      fetchHotelImages();
    } catch (error) {
      console.error('Failed to set cover image:', error);
    }
  };

  const handleDeleteImage = async (imageId: number) => {
    if (!confirm('Are you sure you want to delete this image?')) return;

    try {
      await apiService.deleteHotelImage(imageId);
      fetchHotelImages();
    } catch (error) {
      console.error('Failed to delete image:', error);
    }
  };

  const handleDragStart = (e: any, image: any) => {
    setDraggedItem(image);
  };

  const handleDragOver = (e: any) => {
    e.preventDefault();
  };

  const handleDrop = async (e: any, targetImage: any) => {
    e.preventDefault();
    if (!draggedItem || draggedItem.id === targetImage.id) return;

    const newImages = [...hotelImages];
    const draggedIndex = newImages.findIndex(img => img.id === draggedItem.id);
    const targetIndex = newImages.findIndex(img => img.id === targetImage.id);

    newImages.splice(draggedIndex, 1);
    newImages.splice(targetIndex, 0, draggedItem);

    const reorderData = newImages.map((img, index) => ({ id: img.id, order: index + 1 }));

    try {
      await apiService.reorderHotelImages(reorderData);
      setHotelImages(newImages);
    } catch (error) {
      console.error('Failed to reorder images:', error);
    }

    setDraggedItem(null);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Hotel Image Management</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Hotel Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Select Hotel</label>
            <Select value={selectedHotel} onValueChange={setSelectedHotel}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a hotel..." />
              </SelectTrigger>
              <SelectContent>
                {hotels.map((hotel: any) => (
                  <SelectItem key={hotel.id} value={hotel.id.toString()}>
                    {hotel.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {selectedHotel && (
            <>
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">Upload Images</label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    multiple
                    accept="image/jpeg,image/png"
                    onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md cursor-pointer hover:bg-blue-700"
                  >
                    <Upload className="h-4 w-4" />
                    Choose Files
                  </label>
                  <span className="text-sm text-gray-600">JPEG/PNG, max 5MB each</span>
                </div>
              </div>

              {/* URL Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">Upload from URL</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter image URL..."
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                  />
                  <Button onClick={handleUrlUpload} disabled={!imageUrl}>
                    <Link className="h-4 w-4 mr-2" />
                    Upload
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Images Grid */}
      {selectedHotel && (
        <Card>
          <CardHeader>
            <CardTitle>Hotel Images ({hotelImages.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-32 bg-gray-200 rounded-lg" />
                  </div>
                ))}
              </div>
            ) : hotelImages.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {hotelImages.map((image: any) => (
                  <div 
                    key={image.id} 
                    className="relative group cursor-move"
                    draggable
                    onDragStart={(e) => handleDragStart(e, image)}
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, image)}
                  >
                    <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                      <GripVertical className="h-4 w-4 text-white bg-black/50 rounded" />
                    </div>
                    <img
                      src={`https://skylytapi.scaleitpro.com${image.image_url}`}
                      alt="Hotel"
                      className="w-full h-32 object-cover rounded-lg"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2">
                      <Button
                        size="sm"
                        variant={image.is_cover ? "default" : "secondary"}
                        onClick={() => handleSetCover(image.id)}
                      >
                        {image.is_cover ? <Star className="h-4 w-4" /> : <StarOff className="h-4 w-4" />}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteImage(image.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    {image.is_cover && (
                      <div className="absolute top-2 left-2 bg-yellow-500 text-white px-2 py-1 rounded text-xs">
                        Cover
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No images uploaded for this hotel yet.
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default HotelImageManagement;