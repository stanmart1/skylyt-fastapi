import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Check, ChevronsUpDown, Car, Users, Calendar, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface AddCarBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const AddCarBookingModal = ({ isOpen, onClose, onSuccess }: AddCarBookingModalProps) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingCars, setLoadingCars] = useState(false);
  const [users, setUsers] = useState<any[]>([]);
  const [cars, setCars] = useState<any[]>([]);
  const [usersReady, setUsersReady] = useState(false);
  const [carsReady, setCarsReady] = useState(false);
  const [userSearchOpen, setUserSearchOpen] = useState(false);
  const [carSearchOpen, setCarSearchOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedCar, setSelectedCar] = useState(null);
  const [userSearch, setUserSearch] = useState('');
  const [carSearch, setCarSearch] = useState('');
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    startDate: '',
    endDate: '',
    specialRequests: ''
  });

  useEffect(() => {
    if (isOpen) {
      setUsers([]);
      setCars([]);
      setUsersReady(false);
      setCarsReady(false);
      setSelectedUser(null);
      setSelectedCar(null);
      fetchUsers();
      fetchCars();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    setUsersReady(false);
    try {
      const data = await apiService.getUsers();
      const usersList = data?.users || data;
      const validUsers = Array.isArray(usersList) ? usersList.filter(u => u && u.id) : [];
      setUsers(validUsers);
      setUsersReady(true);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setUsers([]);
      setUsersReady(true);
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchCars = async () => {
    setLoadingCars(true);
    setCarsReady(false);
    try {
      const data = await apiService.searchCars({ limit: 100 });
      const carsList = data?.cars;
      const validCars = Array.isArray(carsList) ? carsList.filter(c => c && c.id) : [];
      setCars(validCars);
      setCarsReady(true);
    } catch (error) {
      console.error('Failed to fetch cars:', error);
      setCars([]);
      setCarsReady(true);
    } finally {
      setLoadingCars(false);
    }
  };

  const handleUserSelect = (user) => {
    if (!user) return;
    setSelectedUser(user);
    setFormData(prev => ({
      ...prev,
      firstName: user.first_name || '',
      lastName: user.last_name || '',
      email: user.email || ''
    }));
    setUserSearchOpen(false);
  };

  const handleCarSelect = (car) => {
    if (!car) return;
    setSelectedCar(car);
    setCarSearchOpen(false);
  };

  const calculateTotal = () => {
    if (!selectedCar || !formData.startDate || !formData.endDate) return 0;
    
    const startDate = new Date(formData.startDate);
    const endDate = new Date(formData.endDate);
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (days <= 0) return 0;
    
    const subtotal = (selectedCar.price || 0) * days;
    const taxes = subtotal * 0.12;
    return subtotal + taxes;
  };

  const handleSubmit = async () => {
    if (!selectedUser || !selectedCar || !formData.startDate || !formData.endDate) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const bookingPayload = {
        user_id: selectedUser.id,
        booking_type: 'car',
        status: 'pending',
        car_name: selectedCar.name || 'Unknown Car',
        total_amount: calculateTotal(),
        currency: 'NGN',
        booking_data: {
          item_id: selectedCar.id,
          guest_name: `${formData.firstName} ${formData.lastName}`,
          guest_email: formData.email,
          special_requests: formData.specialRequests,
          pickup_location: selectedCar.location || 'Default Location',
          start_date: formData.startDate,
          end_date: formData.endDate
        }
      };

      await apiService.createAdminBooking(bookingPayload);
      
      toast({
        title: "Success",
        description: "Car booking created successfully"
      });
      
      onSuccess();
      handleClose();
    } catch (error) {
      console.error('Failed to create booking:', error);
      toast({
        title: "Error",
        description: "Failed to create booking. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedUser(null);
    setSelectedCar(null);
    setUserSearch('');
    setCarSearch('');
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      startDate: '',
      endDate: '',
      specialRequests: ''
    });
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Car className="h-5 w-5" />
            Add Car Booking
          </DialogTitle>
          <DialogDescription>
            Create a new car rental booking for a user
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {(loadingUsers || loadingCars) && (
            <div className="text-center py-4">
              <div className="text-sm text-gray-600">Loading data...</div>
            </div>
          )}

          {/* User Selection */}
          <div className="space-y-2">
            <Label>Select User *</Label>
            <Popover open={userSearchOpen} onOpenChange={setUserSearchOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={userSearchOpen}
                  className="w-full justify-between"
                >
                  {selectedUser ? `${selectedUser.first_name || ''} ${selectedUser.last_name || ''} (${selectedUser.email || ''})` : "Search users..."}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                {loadingUsers ? (
                  <div className="p-4 text-center text-sm text-gray-600">Loading users...</div>
                ) : (
                  <div className="p-2">
                    <div className="flex items-center border-b px-3 pb-2">
                      <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                      <Input
                        placeholder="Search users..."
                        value={userSearch}
                        onChange={(e) => setUserSearch(e.target.value)}
                        className="border-0 p-0 focus-visible:ring-0"
                      />
                    </div>
                    <div className="max-h-48 overflow-y-auto mt-2">
                      {users && users.length > 0 ? (
                        users
                          .filter(user => 
                            user && (
                              (user.first_name || '').toLowerCase().includes(userSearch.toLowerCase()) ||
                              (user.last_name || '').toLowerCase().includes(userSearch.toLowerCase()) ||
                              (user.email || '').toLowerCase().includes(userSearch.toLowerCase())
                            )
                          )
                          .map((user) => (
                            <div
                              key={user?.id || Math.random()}
                              className="flex items-center px-2 py-2 cursor-pointer hover:bg-gray-100 rounded"
                              onClick={() => handleUserSelect(user)}
                            >
                              <Check
                                className={`mr-2 h-4 w-4 ${
                                  selectedUser?.id === user?.id ? "opacity-100" : "opacity-0"
                                }`}
                              />
                              <span className="text-sm">
                                {user?.first_name || ''} {user?.last_name || ''} ({user?.email || ''})
                              </span>
                            </div>
                          ))
                      ) : (
                        <div className="p-2 text-sm text-gray-500">No users available</div>
                      )}
                    </div>
                  </div>
                )}
              </PopoverContent>
            </Popover>
          </div>

          {/* Car Selection */}
          <div className="space-y-2">
            <Label>Select Car *</Label>
            <Popover open={carSearchOpen} onOpenChange={setCarSearchOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={carSearchOpen}
                  className="w-full justify-between"
                >
                  {selectedCar ? `${selectedCar.name || 'Unknown Car'} - ₦${(selectedCar.price || 0).toLocaleString()}/day` : "Search cars..."}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                {loadingCars ? (
                  <div className="p-4 text-center text-sm text-gray-600">Loading cars...</div>
                ) : (
                  <div className="p-2">
                    <div className="flex items-center border-b px-3 pb-2">
                      <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                      <Input
                        placeholder="Search cars..."
                        value={carSearch}
                        onChange={(e) => setCarSearch(e.target.value)}
                        className="border-0 p-0 focus-visible:ring-0"
                      />
                    </div>
                    <div className="max-h-48 overflow-y-auto mt-2">
                      {cars && cars.length > 0 ? (
                        cars
                          .filter(car => 
                            car && (car.name || '').toLowerCase().includes(carSearch.toLowerCase())
                          )
                          .map((car) => (
                            <div
                              key={car?.id || Math.random()}
                              className="flex items-center px-2 py-2 cursor-pointer hover:bg-gray-100 rounded"
                              onClick={() => handleCarSelect(car)}
                            >
                              <Check
                                className={`mr-2 h-4 w-4 ${
                                  selectedCar?.id === car?.id ? "opacity-100" : "opacity-0"
                                }`}
                              />
                              <span className="text-sm">
                                {car?.name || 'Unknown Car'} - ₦{(car?.price || 0).toLocaleString()}/day
                              </span>
                            </div>
                          ))
                      ) : (
                        <div className="p-2 text-sm text-gray-500">No cars available</div>
                      )}
                    </div>
                  </div>
                )}
              </PopoverContent>
            </Popover>
          </div>

          {/* Personal Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="firstName">First Name *</Label>
              <Input
                id="firstName"
                value={formData.firstName}
                onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                placeholder="First name"
              />
            </div>
            <div>
              <Label htmlFor="lastName">Last Name *</Label>
              <Input
                id="lastName"
                value={formData.lastName}
                onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                placeholder="Last name"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="email">Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              placeholder="Email address"
            />
          </div>

          {/* Rental Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="startDate">Start Date *</Label>
              <Input
                id="startDate"
                type="date"
                value={formData.startDate}
                onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
              />
            </div>
            <div>
              <Label htmlFor="endDate">End Date *</Label>
              <Input
                id="endDate"
                type="date"
                value={formData.endDate}
                onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="specialRequests">Special Requests</Label>
            <Textarea
              id="specialRequests"
              value={formData.specialRequests}
              onChange={(e) => setFormData(prev => ({ ...prev, specialRequests: e.target.value }))}
              placeholder="Any special requirements..."
            />
          </div>

          {/* Price Summary */}
          {selectedCar && formData.startDate && formData.endDate && calculateTotal() > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Booking Summary</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Car:</span>
                  <span>{selectedCar.name || 'Unknown Car'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Price per day:</span>
                  <span>₦{(selectedCar.price || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between font-semibold text-lg border-t pt-2">
                  <span>Total:</span>
                  <span>₦{Math.round(calculateTotal()).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-4">
            <Button onClick={handleSubmit} disabled={loading} className="flex-1">
              {loading ? 'Creating...' : 'Create Booking'}
            </Button>
            <Button variant="outline" onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddCarBookingModal;