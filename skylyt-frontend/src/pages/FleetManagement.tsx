import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Car, 
  Search, 
  Plus,
  Edit,
  Trash2,
  Settings,
  Users,
  Fuel,
  Calendar
} from 'lucide-react';
import Navigation from '@/components/Navigation';

const FleetManagement = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const cars = [
    {
      id: 1,
      name: 'BMW 3 Series',
      model: '2023',
      licensePlate: 'ABC-123',
      status: 'Available',
      category: 'Luxury',
      pricePerDay: 89,
      mileage: 12543,
      nextMaintenance: '2024-02-15',
      bookings: 45
    },
    {
      id: 2,
      name: 'Mercedes C-Class',
      model: '2023',
      licensePlate: 'DEF-456',
      status: 'Rented',
      category: 'Luxury',
      pricePerDay: 95,
      mileage: 8765,
      nextMaintenance: '2024-01-20',
      bookings: 52
    },
    {
      id: 3,
      name: 'Toyota Camry',
      model: '2022',
      licensePlate: 'GHI-789',
      status: 'Maintenance',
      category: 'Economy',
      pricePerDay: 65,
      mileage: 25432,
      nextMaintenance: '2024-01-10',
      bookings: 78
    },
    {
      id: 4,
      name: 'Audi A4',
      model: '2023',
      licensePlate: 'JKL-012',
      status: 'Available',
      category: 'Luxury',
      pricePerDay: 85,
      mileage: 15678,
      nextMaintenance: '2024-03-01',
      bookings: 38
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Available':
        return 'bg-green-100 text-green-800';
      case 'Rented':
        return 'bg-blue-100 text-blue-800';
      case 'Maintenance':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredCars = cars.filter(car =>
    car.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    car.licensePlate.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/admin')}
              className="mr-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Admin
            </Button>
            <h1 className="text-3xl font-bold">Fleet Management</h1>
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Add New Vehicle
          </Button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Vehicles</p>
                  <p className="text-2xl font-bold">{cars.length}</p>
                </div>
                <Car className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Available</p>
                  <p className="text-2xl font-bold text-green-600">
                    {cars.filter(car => car.status === 'Available').length}
                  </p>
                </div>
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <div className="w-4 h-4 bg-green-600 rounded-full"></div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Rented</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {cars.filter(car => car.status === 'Rented').length}
                  </p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Maintenance</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {cars.filter(car => car.status === 'Maintenance').length}
                  </p>
                </div>
                <Settings className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by name or license plate..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline">Filter</Button>
            </div>
          </CardContent>
        </Card>

        {/* Vehicle List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredCars.map((car) => (
            <Card key={car.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{car.name}</CardTitle>
                  <Badge className={getStatusColor(car.status)}>
                    {car.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{car.model} • {car.licensePlate}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Category</p>
                      <p className="font-medium">{car.category}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Price/Day</p>
                      <p className="font-medium">${car.pricePerDay}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center">
                      <Fuel className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{car.mileage.toLocaleString()} miles</span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{car.bookings} bookings</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t">
                    <p className="text-sm text-gray-600 mb-2">Next Maintenance: {car.nextMaintenance}</p>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" className="flex-1">
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FleetManagement;