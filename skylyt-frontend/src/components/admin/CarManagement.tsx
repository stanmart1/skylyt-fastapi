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
  make: string;
  model: string;
  category: string;
  price_per_day: number;
  currency: string;
  image_url: string;
  passengers: number;
  transmission: string;
  fuel_type: string;
  plate_number: string;
  year: number;
  status: 'available' | 'booked' | 'out_with_customer' | 'maintenance' | 'out_of_service';
  features: string[];
  is_featured: boolean;
  current_mileage: number;
  insurance_expiry: string;
  registration_expiry: string;
  roadworthiness_expiry: string;
  insurance_doc_url: string;
  registration_doc_url: string;
  roadworthiness_doc_url: string;
  created_at: string;
}

interface MaintenanceRecord {
  id: string;
  car_id: string;
  maintenance_type: string;
  description: string;
  cost: number;
  currency: string;
  scheduled_date: string;
  completed_date?: string;
  next_due_date?: string;
  next_due_mileage?: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  service_provider?: string;
  notes?: string;
  car_name?: string;
}

interface MaintenanceAlerts {
  overdue_maintenance: number;
  upcoming_maintenance: number;
  expiring_documents: number;
  overdue_records: Array<{
    id: string;
    car_name: string;
    maintenance_type: string;
    due_date: string;
  }>;
  upcoming_records: Array<{
    id: string;
    car_name: string;
    maintenance_type: string;
    due_date: string;
  }>;
  expiring_docs: Array<{
    car_id: string;
    car_name: string;
    insurance_expiry?: string;
    registration_expiry?: string;
    roadworthiness_expiry?: string;
  }>;
}

export const CarManagement: React.FC = () => {
  const { currency } = useCurrency();
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [cars, setCars] = useState<CarData[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [maintenanceAlerts, setMaintenanceAlerts] = useState<MaintenanceAlerts | null>(null);
  const [documentFiles, setDocumentFiles] = useState<{
    insurance?: File;
    registration?: File;
    roadworthiness?: File;
  }>({});
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
    make: '',
    model: '',
    category: '',
    price_per_day: 0,
    currency: 'NGN',
    image_url: '',
    passengers: 4,
    transmission: 'automatic',
    fuel_type: 'petrol',
    plate_number: '',
    year: new Date().getFullYear(),
    status: 'available' as const,
    features: '',
    current_mileage: 0,
    insurance_expiry: '',
    registration_expiry: '',
    roadworthiness_expiry: ''
  });
  const [maintenanceForm, setMaintenanceForm] = useState({
    car_id: '',
    maintenance_type: '',
    description: '',
    cost: 0,
    currency: 'NGN',
    scheduled_date: '',
    next_due_date: '',
    next_due_mileage: 0,
    service_provider: '',
    notes: ''
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
    fetchMaintenanceAlerts();
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

  const fetchMaintenanceAlerts = async () => {
    try {
      const data = await apiService.request('/admin/cars/maintenance/alerts');
      setMaintenanceAlerts(data);
    } catch (error) {
      console.error('Failed to fetch maintenance alerts:', error);
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
      make: '',
      model: '',
      category: '',
      price_per_day: 0,
      currency: 'NGN',
      image_url: '',
      passengers: 4,
      transmission: 'automatic',
      fuel_type: 'petrol',
      plate_number: '',
      year: new Date().getFullYear(),
      status: 'available',
      features: '',
      current_mileage: 0,
      insurance_expiry: '',
      registration_expiry: '',
      roadworthiness_expiry: ''
    });
    setDocumentFiles({});
    setCarImageFile(null);
    setIsModalOpen(true);
  };

  const handleEditCar = (car: CarData) => {
    setEditingCar(car);
    setCarForm({
      name: car.name,
      make: car.make || '',
      model: car.model || '',
      category: car.category,
      price_per_day: car.price_per_day || car.price || 0,
      currency: 'NGN',
      image_url: car.image_url || '',
      passengers: car.passengers,
      transmission: car.transmission,
      fuel_type: car.fuel_type || 'petrol',
      plate_number: car.plate_number || '',
      year: car.year || new Date().getFullYear(),
      status: car.status,
      features: car.features?.join(', ') || '',
      current_mileage: car.current_mileage || 0,
      insurance_expiry: car.insurance_expiry ? car.insurance_expiry.split('T')[0] : '',
      registration_expiry: car.registration_expiry ? car.registration_expiry.split('T')[0] : '',
      roadworthiness_expiry: car.roadworthiness_expiry ? car.roadworthiness_expiry.split('T')[0] : ''
    });
    setDocumentFiles({});
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
      
      // Upload documents
      if (documentFiles.insurance) {
        const formData = new FormData();
        formData.append('file', documentFiles.insurance);
        formData.append('upload_type', 'documents');
        const response = await apiService.uploadFile(formData);
        finalCarData.insurance_doc_url = response.url;
      }
      
      if (documentFiles.registration) {
        const formData = new FormData();
        formData.append('file', documentFiles.registration);
        formData.append('upload_type', 'documents');
        const response = await apiService.uploadFile(formData);
        finalCarData.registration_doc_url = response.url;
      }
      
      if (documentFiles.roadworthiness) {
        const formData = new FormData();
        formData.append('file', documentFiles.roadworthiness);
        formData.append('upload_type', 'documents');
        const response = await apiService.uploadFile(formData);
        finalCarData.roadworthiness_doc_url = response.url;
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
      maintenance_type: '',
      description: '',
      cost: 0,
      currency: 'NGN',
      scheduled_date: '',
      next_due_date: '',
      next_due_mileage: 0,
      service_provider: '',
      notes: ''
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
      case 'out_with_customer': return 'bg-orange-100 text-orange-800';
      case 'out_of_service': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return <CheckCircle className="h-4 w-4" />;
      case 'booked': return <Clock className="h-4 w-4" />;
      case 'maintenance': return <Wrench className="h-4 w-4" />;
      case 'out_with_customer': return <Users className="h-4 w-4" />;
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
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Total Fleet</p>
                <p className="text-xl sm:text-2xl font-bold">{loading ? '...' : stats.total_cars}</p>
              </div>
              <Car className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Available</p>
                <p className="text-xl sm:text-2xl font-bold text-green-600">{loading ? '...' : stats.available}</p>
              </div>
              <CheckCircle className="h-6 w-6 sm:h-8 sm:w-8 text-green-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Booked</p>
                <p className="text-xl sm:text-2xl font-bold text-blue-600">{loading ? '...' : stats.booked}</p>
              </div>
              <Clock className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Maintenance</p>
                <p className="text-xl sm:text-2xl font-bold text-yellow-600">{loading ? '...' : stats.maintenance}</p>
              </div>
              <Wrench className="h-6 w-6 sm:h-8 sm:w-8 text-yellow-600 self-end sm:self-auto" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-3 sm:p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div className="mb-2 sm:mb-0">
                <p className="text-xs sm:text-sm font-medium text-gray-600">Revenue</p>
                <p className="text-lg sm:text-2xl font-bold text-green-600">
                  {loading ? '...' : <PriceDisplay amount={stats.revenue_today} currency={currency} />}
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
                <p className="text-xs sm:text-sm font-medium text-gray-600">Utilization</p>
                <p className="text-xl sm:text-2xl font-bold text-purple-600">{loading ? '...' : stats.utilization_rate}%</p>
              </div>
              <Users className="h-6 w-6 sm:h-8 sm:w-8 text-purple-600 self-end sm:self-auto" />
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
          ) : cars.length === 0 ? (
            <Card>
              <CardContent className="p-8 sm:p-12 text-center">
                <Car className="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">No cars in fleet</h3>
                <p className="text-sm sm:text-base text-gray-600 mb-6">Get started by adding your first vehicle to the fleet.</p>
                {hasPermission('content.manage_cars') && (
                  <Button onClick={handleAddCar}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Car
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {cars.map((car) => (
                <Card key={car.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4 sm:p-6">
                    {car.image_url ? (
                      <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                        <img src={car.image_url} alt={car.name} className="w-full h-full object-cover" />
                      </div>
                    ) : (
                      <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                        <Car className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-base sm:text-lg truncate pr-2">{car.name}</h3>
                      <Badge className={`${getStatusColor(car.status)} flex-shrink-0 text-xs`}>
                        <span className="hidden sm:inline mr-1">{getStatusIcon(car.status)}</span>
                        <span className="capitalize">{car.status}</span>
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-1 text-sm">{car.category} • {car.year}</p>
                    <p className="text-xs text-gray-500 mb-2 truncate">{car.plate_number || 'No plate number'}</p>
                    <p className="text-base sm:text-lg font-bold text-blue-600 mb-3">
                      <PriceDisplay 
                        amount={car.price_per_day || car.price || 0} 
                        currency="NGN" 
                        isNGNStored={true}
                      />/day
                    </p>
                    <div className="space-y-1 text-xs sm:text-sm text-gray-600 mb-4">
                      <p className="flex flex-wrap gap-1">
                        <span>{car.passengers} passengers</span>
                        <span>•</span>
                        <span className="capitalize">{car.transmission}</span>
                        <span>•</span>
                        <span className="capitalize">{car.fuel_type}</span>
                      </p>
                      <p>{car.current_mileage?.toLocaleString()} km</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {hasPermission('content.manage_cars') && (
                        <Button variant="outline" size="sm" onClick={() => handleEditCar(car)} className="flex-1 sm:flex-none">
                          <Edit className="h-3 w-3 sm:mr-1" />
                          <span className="hidden sm:inline">Edit</span>
                        </Button>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleFeatureCar(car.id)}
                        className={`${car.is_featured ? 'text-yellow-600 hover:text-yellow-700' : 'text-gray-600 hover:text-gray-700'} flex-1 sm:flex-none`}
                      >
                        <Star className={`h-3 w-3 ${car.is_featured ? 'fill-current' : ''} sm:mr-1`} />
                        <span className="hidden sm:inline">{car.is_featured ? 'Featured' : 'Feature'}</span>
                      </Button>
                      {hasPermission('content.manage_cars') && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setDeleteConfirm({ open: true, carId: car.id, carName: car.name })}
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
        </TabsContent>

        <TabsContent value="maintenance" className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <h3 className="text-lg font-semibold">Maintenance Records</h3>
            <Button onClick={handleAddMaintenance} className="w-full sm:w-auto">
              <Plus className="h-4 w-4 mr-2" />
              Add Maintenance
            </Button>
          </div>
          {maintenance.length === 0 ? (
            <Card>
              <CardContent className="p-8 sm:p-12 text-center">
                <Wrench className="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">No maintenance records</h3>
                <p className="text-sm sm:text-base text-gray-600 mb-6">Keep track of your fleet maintenance by adding records.</p>
                <Button onClick={handleAddMaintenance}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add First Record
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {maintenance.map((record) => (
                <Card key={record.id}>
                  <CardContent className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm sm:text-base">{record.maintenance_type}</h4>
                        <p className="text-xs sm:text-sm text-gray-600 mt-1">{record.description}</p>
                        <p className="text-xs text-gray-500 mt-1">Date: {new Date(record.scheduled_date).toLocaleDateString()}</p>
                        {record.car_name && <p className="text-xs text-gray-500">Car: {record.car_name}</p>}
                      </div>
                      <div className="flex sm:flex-col sm:text-right items-center sm:items-end gap-2">
                        <p className="font-semibold text-sm sm:text-base">
                          <PriceDisplay amount={record.cost} currency={currency} />
                        </p>
                        <Badge className={`${record.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'} text-xs`}>
                          {record.status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
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
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto mx-4" aria-describedby="car-dialog-description">
          <DialogHeader>
            <DialogTitle className="text-lg sm:text-xl">{editingCar ? 'Edit Car' : 'Add New Car'}</DialogTitle>
            <DialogDescription id="car-dialog-description" className="text-sm sm:text-base">
              {editingCar ? 'Update the car details below.' : 'Add a new car to your fleet.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" className="text-sm font-medium">Car Name</Label>
                <Input id="name" value={carForm.name} onChange={(e) => setCarForm({...carForm, name: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="category" className="text-sm font-medium">Category</Label>
                <Select value={carForm.category} onValueChange={(value) => setCarForm({...carForm, category: value})}>
                  <SelectTrigger className="mt-1">
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
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="price_per_day" className="text-sm font-medium">Price per day</Label>
                <Input id="price_per_day" type="number" value={carForm.price_per_day} onChange={(e) => setCarForm({...carForm, price_per_day: Number(e.target.value)})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="passengers" className="text-sm font-medium">Passengers</Label>
                <Input id="passengers" type="number" value={carForm.passengers} onChange={(e) => setCarForm({...carForm, passengers: Number(e.target.value)})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="year" className="text-sm font-medium">Year</Label>
                <Input id="year" type="number" value={carForm.year} onChange={(e) => setCarForm({...carForm, year: Number(e.target.value)})} className="mt-1" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="transmission" className="text-sm font-medium">Transmission</Label>
                <Select value={carForm.transmission} onValueChange={(value) => setCarForm({...carForm, transmission: value})}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select transmission" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automatic">Automatic</SelectItem>
                    <SelectItem value="manual">Manual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="fuel_type" className="text-sm font-medium">Fuel Type</Label>
                <Select value={carForm.fuel_type} onValueChange={(value) => setCarForm({...carForm, fuel_type: value})}>
                  <SelectTrigger className="mt-1">
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="plate_number" className="text-sm font-medium">Plate Number</Label>
                <Input id="plate_number" value={carForm.plate_number} onChange={(e) => setCarForm({...carForm, plate_number: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="mileage" className="text-sm font-medium">Mileage (km)</Label>
                <Input id="mileage" type="number" value={carForm.mileage} onChange={(e) => setCarForm({...carForm, mileage: Number(e.target.value.replace(/,/g, ''))})} className="mt-1" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="insurance_expiry" className="text-sm font-medium">Insurance Expiry</Label>
                <Input id="insurance_expiry" type="date" value={carForm.insurance_expiry} onChange={(e) => setCarForm({...carForm, insurance_expiry: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="registration_expiry" className="text-sm font-medium">Registration Expiry</Label>
                <Input id="registration_expiry" type="date" value={carForm.registration_expiry} onChange={(e) => setCarForm({...carForm, registration_expiry: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="roadworthiness_expiry" className="text-sm font-medium">Roadworthiness Expiry</Label>
                <Input id="roadworthiness_expiry" type="date" value={carForm.roadworthiness_expiry} onChange={(e) => setCarForm({...carForm, roadworthiness_expiry: e.target.value})} className="mt-1" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="insurance_doc" className="text-sm font-medium">Insurance Document</Label>
                <input
                  id="insurance_doc"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setDocumentFiles({...documentFiles, insurance: e.target.files?.[0]})}
                  className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              <div>
                <Label htmlFor="registration_doc" className="text-sm font-medium">Registration Document</Label>
                <input
                  id="registration_doc"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setDocumentFiles({...documentFiles, registration: e.target.files?.[0]})}
                  className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              <div>
                <Label htmlFor="roadworthiness_doc" className="text-sm font-medium">Roadworthiness Document</Label>
                <input
                  id="roadworthiness_doc"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setDocumentFiles({...documentFiles, roadworthiness: e.target.files?.[0]})}
                  className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-1 gap-4">
              <div>
                <Label htmlFor="status" className="text-sm font-medium">Status</Label>
                <Select value={carForm.status} onValueChange={(value: any) => setCarForm({...carForm, status: value})}>
                  <SelectTrigger className="mt-1">
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
              <Label htmlFor="car_image" className="text-sm font-medium">Car Image</Label>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 mt-1">
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
                  className="w-full sm:w-auto"
                >
                  {uploadingCarImage ? 'Uploading...' : 'Choose File'}
                </Button>
                {carImageFile && <span className="text-sm text-gray-600 truncate">{carImageFile.name}</span>}
              </div>
            </div>
            <div>
              <Label htmlFor="features" className="text-sm font-medium">Features (comma separated)</Label>
              <Input id="features" value={carForm.features} onChange={(e) => setCarForm({...carForm, features: e.target.value})} placeholder="GPS, AC, Bluetooth" className="mt-1" />
            </div>
            <div className="flex flex-col sm:flex-row gap-2 pt-4">
              <Button onClick={handleSaveCar} className="w-full sm:w-auto" disabled={uploadingCarImage}>
                {uploadingCarImage ? 'Uploading...' : (editingCar ? 'Update Car' : 'Add Car')}
              </Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)} className="w-full sm:w-auto">Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Maintenance Modal */}
      <Dialog open={isMaintenanceModalOpen} onOpenChange={setIsMaintenanceModalOpen}>
        <DialogContent className="max-w-md mx-4" aria-describedby="maintenance-dialog-description">
          <DialogHeader>
            <DialogTitle className="text-lg">Add Maintenance Record</DialogTitle>
            <DialogDescription id="maintenance-dialog-description" className="text-sm">
              Record maintenance activities for your fleet.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="maintenance_car" className="text-sm font-medium">Car</Label>
              <Select value={maintenanceForm.car_id} onValueChange={(value) => setMaintenanceForm({...maintenanceForm, car_id: value})}>
                <SelectTrigger className="mt-1">
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
              <Label htmlFor="maintenance_type" className="text-sm font-medium">Type</Label>
              <Select value={maintenanceForm.type} onValueChange={(value) => setMaintenanceForm({...maintenanceForm, type: value})}>
                <SelectTrigger className="mt-1">
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
              <Label htmlFor="maintenance_description" className="text-sm font-medium">Description</Label>
              <Input id="maintenance_description" value={maintenanceForm.description} onChange={(e) => setMaintenanceForm({...maintenanceForm, description: e.target.value})} className="mt-1" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="maintenance_cost" className="text-sm font-medium">Cost</Label>
                <Input id="maintenance_cost" type="number" value={maintenanceForm.cost} onChange={(e) => setMaintenanceForm({...maintenanceForm, cost: Number(e.target.value)})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="maintenance_date" className="text-sm font-medium">Date</Label>
                <Input id="maintenance_date" type="date" value={maintenanceForm.date} onChange={(e) => setMaintenanceForm({...maintenanceForm, date: e.target.value})} className="mt-1" />
              </div>
            </div>
            <div>
              <Label htmlFor="next_due" className="text-sm font-medium">Next Due Date</Label>
              <Input id="next_due" type="date" value={maintenanceForm.next_due} onChange={(e) => setMaintenanceForm({...maintenanceForm, next_due: e.target.value})} className="mt-1" />
            </div>
            <div className="flex flex-col sm:flex-row gap-2 pt-4">
              <Button onClick={handleSaveMaintenance} className="w-full sm:w-auto">Add Record</Button>
              <Button variant="outline" onClick={() => setIsMaintenanceModalOpen(false)} className="w-full sm:w-auto">Cancel</Button>
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