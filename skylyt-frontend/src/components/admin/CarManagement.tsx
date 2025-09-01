import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus, Edit, Trash2, Star, Car } from 'lucide-react';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';

export const CarManagement: React.FC = () => {
  const { currency } = useCurrency();
  const { toast } = useToast();
  const [cars, setCars] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCar, setEditingCar] = useState<any>(null);
  const [carForm, setCarForm] = useState({
    name: '',
    category: '',
    price: 0,
    image_url: '',
    passengers: 4,
    transmission: 'automatic',
    features: ''
  });
  const [carImageFile, setCarImageFile] = useState<File | null>(null);
  const [uploadingCarImage, setUploadingCarImage] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; carId: string; carName: string }>({
    open: false,
    carId: '',
    carName: ''
  });

  useEffect(() => {
    fetchCars();
  }, []);

  const fetchCars = async () => {
    try {
      const data = await apiService.request('/admin/cars');
      setCars(data);
    } catch (error) {
      console.error('Failed to fetch cars:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch cars',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddCar = () => {
    setEditingCar(null);
    setCarForm({ name: '', category: '', price: 0, image_url: '', passengers: 4, transmission: 'automatic', features: '' });
    setCarImageFile(null);
    setIsModalOpen(true);
  };

  const handleEditCar = (car: any) => {
    setEditingCar(car);
    setCarForm({
      name: car.name,
      category: car.category,
      price: car.price,
      image_url: car.image_url || '',
      passengers: car.passengers,
      transmission: car.transmission,
      features: car.features.join(', ')
    });
    setCarImageFile(null);
    setIsModalOpen(true);
  };

  const handleCarImageUpload = async (file: File): Promise<string> => {
    setUploadingCarImage(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('upload_type', 'cars');
      
      const response = await apiService.uploadFile(formData);
      const imageUrl = response.url;
      return imageUrl;
    } catch (error) {
      console.error('Failed to upload image:', error);
      toast({
        title: 'Error',
        description: 'Failed to upload image',
        variant: 'error'
      });
      return '';
    } finally {
      setUploadingCarImage(false);
    }
  };

  const handleSaveCar = async () => {
    try {
      let finalCarData = { ...carForm, features: carForm.features.split(',').map(f => f.trim()).filter(f => f) };
      
      // Upload image if selected
      if (carImageFile) {
        const imageUrl = await handleCarImageUpload(carImageFile);
        if (imageUrl) {
          finalCarData.image_url = imageUrl;
        }
      }
      
      if (editingCar) {
        await apiService.request(`/admin/cars/${editingCar.id}`, { method: 'PUT', body: JSON.stringify(finalCarData) });
        toast({
          title: 'Success',
          description: 'Car updated successfully',
          variant: 'success'
        });
      } else {
        await apiService.request('/admin/cars', { method: 'POST', body: JSON.stringify(finalCarData) });
        toast({
          title: 'Success',
          description: 'Car added successfully',
          variant: 'success'
        });
      }
      await fetchCars();
      setIsModalOpen(false);
      setCarImageFile(null);
    } catch (error) {
      console.error('Failed to save car:', error);
      toast({
        title: 'Error',
        description: 'Failed to save car',
        variant: 'error'
      });
    }
  };

  const handleDeleteCar = async () => {
    try {
      await apiService.request(`/admin/cars/${deleteConfirm.carId}`, { method: 'DELETE' });
      await fetchCars();
      toast({
        title: 'Success',
        description: 'Car deleted successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to delete car:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete car',
        variant: 'error'
      });
    }
  };

  const handleFeatureCar = async (carId: string) => {
    try {
      await apiService.request(`/admin/cars/${carId}/feature`, { method: 'POST' });
      await fetchCars();
      toast({
        title: 'Success',
        description: 'Car feature status updated',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to feature car:', error);
      toast({
        title: 'Error',
        description: 'Failed to update car feature status',
        variant: 'error'
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Car Management</h2>
        <Button onClick={handleAddCar}>
          <Plus className="h-4 w-4 mr-2" />
          Add Car
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
          {cars.map((car) => (
            <Card key={car.id}>
              <CardContent className="p-6">
                {car.image_url ? (
                  <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                    <img src={car.image_url} alt={car.name} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                    <Car className="h-8 w-8 text-gray-400" />
                  </div>
                )}
                <h3 className="font-semibold text-lg">{car.name}</h3>
                <p className="text-gray-600 mb-2">{car.category}</p>
                <p className="text-lg font-bold text-blue-600">
                  <PriceDisplay amount={car.price} currency={car.currency || currency} />/day
                </p>
                <div className="mt-4 space-y-1 text-sm text-gray-600">
                  <p>{car.passengers} passengers • {car.transmission}</p>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" onClick={() => handleEditCar(car)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleFeatureCar(car.id)}
                    className={car.is_featured ? 'text-yellow-600 hover:text-yellow-700' : 'text-gray-600 hover:text-gray-700'}
                  >
                    <Star className={`h-3 w-3 ${car.is_featured ? 'fill-current' : ''}`} />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setDeleteConfirm({ open: true, carId: car.id, carName: car.name })}
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
            <DialogTitle>{editingCar ? 'Edit Car' : 'Add New Car'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Car Name</Label>
              <Input id="name" value={carForm.name} onChange={(e) => setCarForm({...carForm, name: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Input id="category" value={carForm.category} onChange={(e) => setCarForm({...carForm, category: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="price">Price per day</Label>
                <Input id="price" type="number" value={carForm.price} onChange={(e) => setCarForm({...carForm, price: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="passengers">Passengers</Label>
                <Input id="passengers" type="number" value={carForm.passengers} onChange={(e) => setCarForm({...carForm, passengers: Number(e.target.value)})} />
              </div>
            </div>
            <div>
              <Label htmlFor="transmission">Transmission</Label>
              <Input id="transmission" value={carForm.transmission} onChange={(e) => setCarForm({...carForm, transmission: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="car_image">Car Image</Label>
              <div className="flex items-center gap-2">
                <input
                  id="car_image"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setCarImageFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('car_image')?.click()}
                  disabled={uploadingCarImage}
                >
                  {uploadingCarImage ? 'Uploading...' : 'Choose File'}
                </Button>
                {carImageFile && <span className="text-sm text-gray-600">{carImageFile.name}</span>}
              </div>
            </div>
            <div>
              <Label htmlFor="features">Features (comma separated)</Label>
              <Input id="features" value={carForm.features} onChange={(e) => setCarForm({...carForm, features: e.target.value})} placeholder="GPS, AC, Bluetooth" />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveCar}>{editingCar ? 'Update Car' : 'Add Car'}</Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteConfirm.open}
        onOpenChange={(open) => setDeleteConfirm({ ...deleteConfirm, open })}
        title="Delete Car"
        description={`Are you sure you want to delete "${deleteConfirm.carName}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="destructive"
        onConfirm={handleDeleteCar}
      />
    </div>
  );
};