import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Car, Plus, Edit, Trash2, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';

interface CarData {
  id: number;
  name: string;
  category: string;
  price: number;
  image_url?: string;
  passengers: number;
  transmission: string;
  features: string[];
}

const CarManagement = () => {
  const [cars, setCars] = useState<CarData[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCar, setEditingCar] = useState<CarData | null>(null);
  const [carForm, setCarForm] = useState({
    name: '',
    category: '',
    price: 0,
    image_url: '',
    passengers: 4,
    transmission: 'automatic',
    features: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchCars();
  }, []);

  const fetchCars = async () => {
    try {
      const data = await apiService.request('/admin/cars');
      setCars(data);
    } catch (error) {
      console.error('Failed to fetch cars:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCar = () => {
    setEditingCar(null);
    setCarForm({
      name: '',
      category: '',
      price: 0,
      image_url: '',
      passengers: 4,
      transmission: 'automatic',
      features: ''
    });
    setIsModalOpen(true);
  };

  const handleEditCar = (car: CarData) => {
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
    setIsModalOpen(true);
  };

  const handleSaveCar = async () => {
    try {
      const carData = {
        ...carForm,
        features: carForm.features.split(',').map(f => f.trim()).filter(f => f)
      };

      if (editingCar) {
        await apiService.request(`/admin/cars/${editingCar.id}`, {
          method: 'PUT',
          body: JSON.stringify(carData)
        });
      } else {
        await apiService.request('/admin/cars', {
          method: 'POST',
          body: JSON.stringify(carData)
        });
      }

      await fetchCars();
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to save car:', error);
    }
  };

  const handleDeleteCar = async (carId: number) => {
    if (!confirm('Are you sure you want to delete this car?')) return;

    try {
      await apiService.request(`/admin/cars/${carId}`, { method: 'DELETE' });
      await fetchCars();
    } catch (error) {
      console.error('Failed to delete car:', error);
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
              <h1 className="text-3xl font-bold">Car Management</h1>
              <p className="text-gray-600">Manage your car fleet</p>
            </div>
          </div>
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
                  <div className="flex items-start justify-between mb-4">
                    <Car className="h-8 w-8 text-blue-600" />
                    <Badge className={car.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {car.is_available ? 'Available' : 'Unavailable'}
                    </Badge>
                  </div>
                  <h3 className="font-semibold text-lg">{car.name}</h3>
                  <p className="text-gray-600 mb-2">{car.category}</p>
                  <p className="text-lg font-bold text-blue-600">${car.price}/day</p>
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
                      onClick={() => handleDeleteCar(car.id)}
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

        {/* Add/Edit Car Modal */}
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{editingCar ? 'Edit Car' : 'Add New Car'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Car Name</Label>
                <Input
                  id="name"
                  value={carForm.name}
                  onChange={(e) => setCarForm({...carForm, name: e.target.value})}
                  placeholder="e.g., Toyota Camry 2024"
                />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={carForm.category}
                  onChange={(e) => setCarForm({...carForm, category: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="price">Price per day</Label>
                  <Input
                    id="price"
                    type="number"
                    value={carForm.price}
                    onChange={(e) => setCarForm({...carForm, price: Number(e.target.value)})}
                  />
                </div>
                <div>
                  <Label htmlFor="passengers">Passengers</Label>
                  <Input
                    id="passengers"
                    type="number"
                    value={carForm.passengers}
                    onChange={(e) => setCarForm({...carForm, passengers: Number(e.target.value)})}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="transmission">Transmission</Label>
                <Input
                  id="transmission"
                  value={carForm.transmission}
                  onChange={(e) => setCarForm({...carForm, transmission: e.target.value})}
                  placeholder="automatic, manual"
                />
              </div>
              <div>
                <Label htmlFor="features">Features (comma separated)</Label>
                <Input
                  id="features"
                  value={carForm.features}
                  onChange={(e) => setCarForm({...carForm, features: e.target.value})}
                  placeholder="GPS, AC, Bluetooth"
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button onClick={handleSaveCar}>
                  {editingCar ? 'Update Car' : 'Add Car'}
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

export default CarManagement;