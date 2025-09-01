import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Edit, Trash2, Star, Car, Calendar, Wrench, Users, DollarSign, AlertTriangle, CheckCircle, Clock, Settings } from 'lucide-react';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

interface CarData {
  id: string;
  name: string;
  category: string;
  price: number;
  currency: string;
  image_url: string;
  passengers: number;
  transmission: string;
  fuel_type: string;
  plate_number: string;
  year: number;
  status: 'available' | 'booked' | 'maintenance' | 'out_of_service';
  features: string[];
  is_featured: boolean;
  mileage: number;
  insurance_expiry: string;
  last_service: string;
  next_service: string;
  created_at: string;
}

interface MaintenanceRecord {
  id: string;
  car_id: string;
  type: string;
  description: string;
  cost: number;
  date: string;
  next_due: string;
  status: 'completed' | 'scheduled' | 'overdue';
}

export const CarManagement: React.FC = () => {
  const { currency } = useCurrency();
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [cars, setCars] = useState<CarData[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('fleet');
  const [stats, setStats] = useState({
    total_cars: 0,
    available: 0,
    booked: 0,
    maintenance: 0,
    revenue_today: 0,
    utilization_rate: 0
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCar, setEditingCar] = useState<any>(null);
  const [carForm, setCarForm] = useState({
    name: '',
    category: '',
    price: 0,
    image_url: '',
    passengers: 4,
    transmission: 'automatic',
    fuel_type: 'petrol',
    plate_number: '',
    year: new Date().getFullYear(),
    status: 'available' as const,
    features: '',
    mileage: 0,
    insurance_expiry: '',
    last_service: '',
    next_service: ''
  });
  const [maintenanceForm, setMaintenanceForm] = useState({
    car_id: '',
    type: '',
    description: '',
    cost: 0,
    date: '',
    next_due: ''
  });
  const [isMaintenanceModalOpen, setIsMaintenanceModalOpen] = useState(false);
  const [carImageFile, setCarImageFile] = useState<File | null>(null);
  const [uploadingCarImage, setUploadingCarImage] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; carId: string; carName: string }>({
    open: false,
    carId: '',
    carName: ''
  });

  useEffect(() => {
    fetchCars();
    fetchMaintenance();
    fetchStats();
  }, []);

  const fetchCars = async () => {
    try {
      const data = await apiService.request('/admin/cars');
      setCars(data || []);
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

  const fetchMaintenance = async () => {
    try {
      const data = await apiService.request('/admin/cars/maintenance');
      setMaintenance(data || []);
    } catch (error) {
      console.error('Failed to fetch maintenance records:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await apiService.request('/admin/cars/stats');
      setStats(data || stats);
    } catch (error) {
      console.error('Failed to fetch car stats:', error);
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
      fuel_type: 'petrol',
      plate_number: '',
      year: new Date().getFullYear(),
      status: 'available',
      features: '',
      mileage: 0,
      insurance_expiry: '',
      last_service: '',
      next_service: ''
    });
    setCarImageFile(null);
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
      fuel_type: car.fuel_type || 'petrol',
      plate_number: car.plate_number || '',
      year: car.year || new Date().getFullYear(),
      status: car.status,
      features: car.features?.join(', ') || '',
      mileage: car.mileage || 0,
      insurance_expiry: car.insurance_expiry || '',
      last_service: car.last_service || '',
      next_service: car.next_service || ''
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
      let finalCarData = { 
        ...carForm, 
        features: carForm.features.split(',').map(f => f.trim()).filter(f => f)
      };
      
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
      await fetchStats();
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

  const handleAddMaintenance = () => {
    setMaintenanceForm({
      car_id: '',
      type: '',
      description: '',
      cost: 0,
      date: '',
      next_due: ''
    });
    setIsMaintenanceModalOpen(true);
  };

  const handleSaveMaintenance = async () => {
    try {
      await apiService.request('/admin/cars/maintenance', {
        method: 'POST',
        body: JSON.stringify(maintenanceForm)
      });
      toast({
        title: 'Success',
        description: 'Maintenance record added successfully',
        variant: 'success'
      });
      await fetchMaintenance();
      setIsMaintenanceModalOpen(false);
    } catch (error) {
      console.error('Failed to save maintenance record:', error);
      toast({
        title: 'Error',
        description: 'Failed to save maintenance record',
        variant: 'error'
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'booked': return 'bg-blue-100 text-blue-800';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800';
      case 'out_of_service': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return <CheckCircle className="h-4 w-4" />;
      case 'booked': return <Clock className="h-4 w-4" />;
      case 'maintenance': return <Wrench className="h-4 w-4" />;
      case 'out_of_service': return <AlertTriangle className="h-4 w-4" />;
      default: return <Car className="h-4 w-4" />;
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
        <div>
          <h2 className="text-2xl font-bold">Car Fleet Management</h2>
          <p className="text-gray-600">Manage your vehicle fleet, maintenance, and operations</p>
        </div>
        {hasPermission('content.manage_cars') && (
          <Button onClick={handleAddCar}>
            <Plus className="h-4 w-4 mr-2" />
            Add Car
          </Button>
        )}
      </div>

      {/* Fleet Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Fleet</p>
                <p className="text-2xl font-bold">{stats.total_cars}</p>
              </div>
              <Car className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Available</p>
                <p className="text-2xl font-bold text-green-600">{stats.available}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Booked</p>
                <p className="text-2xl font-bold text-blue-600">{stats.booked}</p>
              </div>
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Maintenance</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.maintenance}</p>
              </div>
              <Wrench className="h-8 w-8 text-yellow-600" />
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
                <p className="text-sm font-medium text-gray-600">Utilization</p>
                <p className="text-2xl font-bold text-purple-600">{stats.utilization_rate}%</p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different sections */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="fleet">Fleet Management</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="fleet" className="space-y-4">

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
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-lg">{car.name}</h3>
                      <Badge className={getStatusColor(car.status)}>
                        {getStatusIcon(car.status)}
                        <span className="ml-1">{car.status}</span>
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-1">{car.category} • {car.year}</p>
                    <p className="text-sm text-gray-500 mb-2">{car.plate_number}</p>
                    <p className="text-lg font-bold text-blue-600">
                      <PriceDisplay amount={car.price} currency={car.currency || currency} />/day
                    </p>
                    <div className="mt-4 space-y-1 text-sm text-gray-600">
                      <p>{car.passengers} passengers • {car.transmission} • {car.fuel_type}</p>
                      <p>{car.mileage?.toLocaleString()} km</p>
                    </div>
                    <div className="flex gap-2 mt-4">
                      {hasPermission('content.manage_cars') && (
                        <Button variant="outline" size="sm" onClick={() => handleEditCar(car)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleFeatureCar(car.id)}
                        className={car.is_featured ? 'text-yellow-600 hover:text-yellow-700' : 'text-gray-600 hover:text-gray-700'}
                      >
                        <Star className={`h-3 w-3 ${car.is_featured ? 'fill-current' : ''}`} />
                      </Button>
                      {hasPermission('content.manage_cars') && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setDeleteConfirm({ open: true, carId: car.id, carName: car.name })}
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

        <TabsContent value="maintenance" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Maintenance Records</h3>
            <Button onClick={handleAddMaintenance}>
              <Plus className="h-4 w-4 mr-2" />
              Add Maintenance
            </Button>
          </div>
          <div className="space-y-4">
            {maintenance.map((record) => (
              <Card key={record.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">{record.type}</h4>
                      <p className="text-sm text-gray-600">{record.description}</p>
                      <p className="text-sm text-gray-500">Date: {new Date(record.date).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        <PriceDisplay amount={record.cost} currency={currency} />
                      </p>
                      <Badge className={record.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                        {record.status}
                      </Badge>
                    </div>
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
                <CardTitle>Fleet Utilization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Available</span>
                    <span>{stats.available} cars</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Booked</span>
                    <span>{stats.booked} cars</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Maintenance</span>
                    <span>{stats.maintenance} cars</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Revenue Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Today</span>
                    <span><PriceDisplay amount={stats.revenue_today} currency={currency} /></span>
                  </div>
                  <div className="flex justify-between">
                    <span>Utilization Rate</span>
                    <span>{stats.utilization_rate}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingCar ? 'Edit Car' : 'Add New Car'}</DialogTitle>
            <DialogDescription>
              {editingCar ? 'Update the car details below.' : 'Add a new car to your fleet.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Car Name</Label>
                <Input id="name" value={carForm.name} onChange={(e) => setCarForm({...carForm, name: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Select value={carForm.category} onValueChange={(value) => setCarForm({...carForm, category: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="economy">Economy</SelectItem>
                    <SelectItem value="compact">Compact</SelectItem>
                    <SelectItem value="midsize">Midsize</SelectItem>
                    <SelectItem value="luxury">Luxury</SelectItem>
                    <SelectItem value="suv">SUV</SelectItem>
                    <SelectItem value="van">Van</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="price">Price per day</Label>
                <Input id="price" type="number" value={carForm.price} onChange={(e) => setCarForm({...carForm, price: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="passengers">Passengers</Label>
                <Input id="passengers" type="number" value={carForm.passengers} onChange={(e) => setCarForm({...carForm, passengers: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="year">Year</Label>
                <Input id="year" type="number" value={carForm.year} onChange={(e) => setCarForm({...carForm, year: Number(e.target.value)})} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="transmission">Transmission</Label>
                <Select value={carForm.transmission} onValueChange={(value) => setCarForm({...carForm, transmission: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select transmission" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automatic">Automatic</SelectItem>
                    <SelectItem value="manual">Manual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="fuel_type">Fuel Type</Label>
                <Select value={carForm.fuel_type} onValueChange={(value) => setCarForm({...carForm, fuel_type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select fuel type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="petrol">Petrol</SelectItem>
                    <SelectItem value="diesel">Diesel</SelectItem>
                    <SelectItem value="electric">Electric</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="plate_number">Plate Number</Label>
                <Input id="plate_number" value={carForm.plate_number} onChange={(e) => setCarForm({...carForm, plate_number: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="mileage">Mileage (km)</Label>
                <Input id="mileage" type="number" value={carForm.mileage} onChange={(e) => setCarForm({...carForm, mileage: Number(e.target.value)})} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="insurance_expiry">Insurance Expiry</Label>
                <Input id="insurance_expiry" type="date" value={carForm.insurance_expiry} onChange={(e) => setCarForm({...carForm, insurance_expiry: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select value={carForm.status} onValueChange={(value: any) => setCarForm({...carForm, status: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="available">Available</SelectItem>
                    <SelectItem value="booked">Booked</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="out_of_service">Out of Service</SelectItem>
                  </SelectContent>
                </Select>
              </div>
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

      {/* Maintenance Modal */}
      <Dialog open={isMaintenanceModalOpen} onOpenChange={setIsMaintenanceModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Maintenance Record</DialogTitle>
            <DialogDescription>
              Record maintenance activities for your fleet.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="maintenance_car">Car</Label>
              <Select value={maintenanceForm.car_id} onValueChange={(value) => setMaintenanceForm({...maintenanceForm, car_id: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select car" />
                </SelectTrigger>
                <SelectContent>
                  {cars.map((car) => (
                    <SelectItem key={car.id} value={car.id}>
                      {car.name} - {car.plate_number}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="maintenance_type">Type</Label>
              <Select value={maintenanceForm.type} onValueChange={(value) => setMaintenanceForm({...maintenanceForm, type: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="oil_change">Oil Change</SelectItem>
                  <SelectItem value="tire_replacement">Tire Replacement</SelectItem>
                  <SelectItem value="brake_service">Brake Service</SelectItem>
                  <SelectItem value="general_service">General Service</SelectItem>
                  <SelectItem value="repair">Repair</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="maintenance_description">Description</Label>
              <Input id="maintenance_description" value={maintenanceForm.description} onChange={(e) => setMaintenanceForm({...maintenanceForm, description: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="maintenance_cost">Cost</Label>
                <Input id="maintenance_cost" type="number" value={maintenanceForm.cost} onChange={(e) => setMaintenanceForm({...maintenanceForm, cost: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="maintenance_date">Date</Label>
                <Input id="maintenance_date" type="date" value={maintenanceForm.date} onChange={(e) => setMaintenanceForm({...maintenanceForm, date: e.target.value})} />
              </div>
            </div>
            <div>
              <Label htmlFor="next_due">Next Due Date</Label>
              <Input id="next_due" type="date" value={maintenanceForm.next_due} onChange={(e) => setMaintenanceForm({...maintenanceForm, next_due: e.target.value})} />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveMaintenance}>Add Record</Button>
              <Button variant="outline" onClick={() => setIsMaintenanceModalOpen(false)}>Cancel</Button>
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