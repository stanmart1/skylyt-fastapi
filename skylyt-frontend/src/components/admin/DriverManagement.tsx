import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Edit, Trash2, User, Phone, Mail, Calendar, Star, CheckCircle, XCircle, Clock, Search, Filter } from 'lucide-react';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

interface Driver {
  id: number;
  name: string;
  email: string;
  phone: string;
  license_number: string;
  license_expiry?: string;
  license_class?: string;
  employee_id?: string;
  hire_date?: string;
  is_available: boolean;
  is_active: boolean;
  rating: number;
  total_trips: number;
  address?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export const DriverManagement: React.FC = () => {
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [filters, setFilters] = useState({
    search: '',
    is_active: '',
    is_available: ''
  });
  const [driverForm, setDriverForm] = useState({
    name: '',
    email: '',
    phone: '',
    license_number: '',
    license_expiry: '',
    license_class: '',
    employee_id: '',
    hire_date: '',
    address: '',
    emergency_contact: '',
    emergency_phone: '',
    notes: ''
  });
  const [deleteConfirm, setDeleteConfirm] = useState<{
    open: boolean;
    driverId: number;
    driverName: string;
  }>({
    open: false,
    driverId: 0,
    driverName: ''
  });

  useEffect(() => {
    fetchDrivers();
  }, [filters]);

  const fetchDrivers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.is_active) params.append('is_active', filters.is_active);
      if (filters.is_available) params.append('is_available', filters.is_available);
      
      const data = await apiService.request(`/drivers?${params.toString()}`);
      setDrivers(data || []);
    } catch (error) {
      console.error('Failed to fetch drivers:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch drivers',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddDriver = () => {
    setEditingDriver(null);
    setDriverForm({
      name: '',
      email: '',
      phone: '',
      license_number: '',
      license_expiry: '',
      license_class: '',
      employee_id: '',
      hire_date: '',
      address: '',
      emergency_contact: '',
      emergency_phone: '',
      notes: ''
    });
    setIsModalOpen(true);
  };

  const handleEditDriver = (driver: Driver) => {
    setEditingDriver(driver);
    setDriverForm({
      name: driver.name,
      email: driver.email,
      phone: driver.phone,
      license_number: driver.license_number,
      license_expiry: driver.license_expiry ? driver.license_expiry.split('T')[0] : '',
      license_class: driver.license_class || '',
      employee_id: driver.employee_id || '',
      hire_date: driver.hire_date ? driver.hire_date.split('T')[0] : '',
      address: driver.address || '',
      emergency_contact: driver.emergency_contact || '',
      emergency_phone: driver.emergency_phone || '',
      notes: driver.notes || ''
    });
    setIsModalOpen(true);
  };

  const handleSaveDriver = async () => {
    try {
      if (editingDriver) {
        await apiService.request(`/drivers/${editingDriver.id}`, {
          method: 'PUT',
          body: JSON.stringify(driverForm)
        });
        toast({
          title: 'Success',
          description: 'Driver updated successfully',
          variant: 'success'
        });
      } else {
        await apiService.request('/drivers', {
          method: 'POST',
          body: JSON.stringify(driverForm)
        });
        toast({
          title: 'Success',
          description: 'Driver added successfully',
          variant: 'success'
        });
      }
      await fetchDrivers();
      setIsModalOpen(false);
    } catch (error: any) {
      console.error('Failed to save driver:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to save driver',
        variant: 'error'
      });
    }
  };

  const handleDeleteDriver = async () => {
    try {
      await apiService.request(`/drivers/${deleteConfirm.driverId}`, {
        method: 'DELETE'
      });
      await fetchDrivers();
      toast({
        title: 'Success',
        description: 'Driver deleted successfully',
        variant: 'success'
      });
    } catch (error: any) {
      console.error('Failed to delete driver:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete driver',
        variant: 'error'
      });
    }
  };

  const handleToggleAvailability = async (driverId: number, isAvailable: boolean) => {
    try {
      await apiService.request(`/drivers/${driverId}/availability`, {
        method: 'PUT',
        body: JSON.stringify({ is_available: !isAvailable })
      });
      await fetchDrivers();
      toast({
        title: 'Success',
        description: `Driver availability updated`,
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to update driver availability:', error);
      toast({
        title: 'Error',
        description: 'Failed to update driver availability',
        variant: 'error'
      });
    }
  };

  const getStatusColor = (isActive: boolean, isAvailable: boolean) => {
    if (!isActive) return 'bg-red-100 text-red-800';
    if (isAvailable) return 'bg-green-100 text-green-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getStatusText = (isActive: boolean, isAvailable: boolean) => {
    if (!isActive) return 'Inactive';
    if (isAvailable) return 'Available';
    return 'Busy';
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-3 w-3 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div></div>
        {hasPermission('content.manage_drivers') && (
          <Button onClick={handleAddDriver}>
            <Plus className="h-4 w-4 mr-2" />
            Add Driver
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search drivers..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-10"
              />
            </div>
            
            <Select value={filters.is_active || 'all'} onValueChange={(value) => setFilters({ ...filters, is_active: value === 'all' ? '' : value })}>
              <SelectTrigger>
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="true">Active</SelectItem>
                <SelectItem value="false">Inactive</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.is_available || 'all'} onValueChange={(value) => setFilters({ ...filters, is_available: value === 'all' ? '' : value })}>
              <SelectTrigger>
                <SelectValue placeholder="All Availability" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Availability</SelectItem>
                <SelectItem value="true">Available</SelectItem>
                <SelectItem value="false">Busy</SelectItem>
              </SelectContent>
            </Select>

            <Button 
              variant="outline" 
              onClick={() => setFilters({ search: '', is_active: '', is_available: '' })}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Drivers List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Drivers ({drivers.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse h-24 bg-gray-200 rounded" />
              ))}
            </div>
          ) : drivers.length === 0 ? (
            <div className="text-center py-8">
              <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No drivers found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {drivers.map((driver) => (
                <div key={driver.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">{driver.name}</h3>
                        <Badge className={`${getStatusColor(driver.is_active, driver.is_available)} text-xs`}>
                          {getStatusText(driver.is_active, driver.is_available)}
                        </Badge>
                        {driver.rating > 0 && (
                          <div className="flex items-center gap-1">
                            {renderStars(Math.round(driver.rating))}
                            <span className="text-sm text-gray-600">({driver.rating.toFixed(1)})</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          <span>{driver.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          <span>{driver.phone}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>License: {driver.license_number}</span>
                        </div>
                        {driver.employee_id && (
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4" />
                            <span>ID: {driver.employee_id}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4" />
                          <span>{driver.total_trips} trips</span>
                        </div>
                        {driver.hire_date && (
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>Hired: {new Date(driver.hire_date).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-2 ml-4">
                      {hasPermission('content.manage_drivers') && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditDriver(driver)}
                          >
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleToggleAvailability(driver.id, driver.is_available)}
                            className={driver.is_available ? 'text-yellow-600' : 'text-green-600'}
                          >
                            {driver.is_available ? (
                              <>
                                <Clock className="h-4 w-4 mr-1" />
                                Set Busy
                              </>
                            ) : (
                              <>
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Set Available
                              </>
                            )}
                          </Button>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setDeleteConfirm({
                              open: true,
                              driverId: driver.id,
                              driverName: driver.name
                            })}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Driver Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingDriver ? 'Edit Driver' : 'Add New Driver'}</DialogTitle>
            <DialogDescription>
              {editingDriver ? 'Update the driver details below.' : 'Add a new driver to your team.'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  value={driverForm.name}
                  onChange={(e) => setDriverForm({ ...driverForm, name: e.target.value })}
                  placeholder="Enter full name"
                />
              </div>
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={driverForm.email}
                  onChange={(e) => setDriverForm({ ...driverForm, email: e.target.value })}
                  placeholder="Enter email address"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="phone">Phone Number *</Label>
                <Input
                  id="phone"
                  value={driverForm.phone}
                  onChange={(e) => setDriverForm({ ...driverForm, phone: e.target.value })}
                  placeholder="Enter phone number"
                />
              </div>
              <div>
                <Label htmlFor="license_number">License Number *</Label>
                <Input
                  id="license_number"
                  value={driverForm.license_number}
                  onChange={(e) => setDriverForm({ ...driverForm, license_number: e.target.value })}
                  placeholder="Enter license number"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="license_expiry">License Expiry</Label>
                <Input
                  id="license_expiry"
                  type="date"
                  value={driverForm.license_expiry}
                  onChange={(e) => setDriverForm({ ...driverForm, license_expiry: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="license_class">License Class</Label>
                <Select value={driverForm.license_class} onValueChange={(value) => setDriverForm({ ...driverForm, license_class: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select class" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="B">Class B</SelectItem>
                    <SelectItem value="C">Class C</SelectItem>
                    <SelectItem value="D">Class D</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="employee_id">Employee ID</Label>
                <Input
                  id="employee_id"
                  value={driverForm.employee_id}
                  onChange={(e) => setDriverForm({ ...driverForm, employee_id: e.target.value })}
                  placeholder="Enter employee ID"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="hire_date">Hire Date</Label>
                <Input
                  id="hire_date"
                  type="date"
                  value={driverForm.hire_date}
                  onChange={(e) => setDriverForm({ ...driverForm, hire_date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="emergency_contact">Emergency Contact</Label>
                <Input
                  id="emergency_contact"
                  value={driverForm.emergency_contact}
                  onChange={(e) => setDriverForm({ ...driverForm, emergency_contact: e.target.value })}
                  placeholder="Emergency contact name"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="emergency_phone">Emergency Phone</Label>
                <Input
                  id="emergency_phone"
                  value={driverForm.emergency_phone}
                  onChange={(e) => setDriverForm({ ...driverForm, emergency_phone: e.target.value })}
                  placeholder="Emergency contact phone"
                />
              </div>
              <div>
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={driverForm.address}
                  onChange={(e) => setDriverForm({ ...driverForm, address: e.target.value })}
                  placeholder="Enter address"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={driverForm.notes}
                onChange={(e) => setDriverForm({ ...driverForm, notes: e.target.value })}
                placeholder="Additional notes about the driver"
                rows={3}
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveDriver}>
                {editingDriver ? 'Update Driver' : 'Add Driver'}
              </Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirm.open}
        onOpenChange={(open) => setDeleteConfirm({ ...deleteConfirm, open })}
        title="Delete Driver"
        description={`Are you sure you want to delete "${deleteConfirm.driverName}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="destructive"
        onConfirm={handleDeleteDriver}
      />
    </div>
  );
};