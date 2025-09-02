import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Check, ChevronsUpDown, Hotel, Users, Calendar } from 'lucide-react';
import { cn } from '@/lib/utils';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface AddHotelBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const AddHotelBookingModal = ({ isOpen, onClose, onSuccess }: AddHotelBookingModalProps) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingHotels, setLoadingHotels] = useState(false);
  const [users, setUsers] = useState<any[]>([]);
  const [hotels, setHotels] = useState<any[]>([]);
  const [userSearchOpen, setUserSearchOpen] = useState(false);
  const [hotelSearchOpen, setHotelSearchOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedHotel, setSelectedHotel] = useState(null);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    checkInDate: '',
    checkOutDate: '',
    numberOfGuests: 1,
    specialRequests: ''
  });

  useEffect(() => {
    if (isOpen) {
      // Reset state first
      setUsers([]);
      setHotels([]);
      setSelectedUser(null);
      setSelectedHotel(null);
      // Then fetch data
      fetchUsers();
      fetchHotels();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const data = await apiService.getUsers();
      // Handle the nested response structure from /rbac/users
      const usersList = data?.users || data || [];
      setUsers(Array.isArray(usersList) ? usersList : []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchHotels = async () => {
    setLoadingHotels(true);
    try {
      const data = await apiService.searchHotels({ limit: 100 });
      const hotelsList = data?.hotels || [];
      setHotels(Array.isArray(hotelsList) ? hotelsList : []);
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
      setHotels([]);
    } finally {
      setLoadingHotels(false);
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

  const handleHotelSelect = (hotel) => {
    if (!hotel) return;
    setSelectedHotel(hotel);
    setHotelSearchOpen(false);
  };

  const calculateTotal = () => {
    if (!selectedHotel || !formData.checkInDate || !formData.checkOutDate) return 0;
    
    const checkIn = new Date(formData.checkInDate);
    const checkOut = new Date(formData.checkOutDate);
    const nights = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24));
    
    if (nights <= 0) return 0;
    
    const subtotal = (selectedHotel.price_per_night || 0) * nights;
    const taxes = subtotal * 0.12;
    return subtotal + taxes;
  };

  const handleSubmit = async () => {
    if (!selectedUser || !selectedHotel || !formData.checkInDate || !formData.checkOutDate) {
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
        booking_type: 'hotel',
        booking_data: {
          item_id: selectedHotel.id,
          guest_name: `${formData.firstName} ${formData.lastName}`,
          guest_email: formData.email,
          special_requests: formData.specialRequests,
          pickup_location: selectedHotel.location,
          number_of_guests: formData.numberOfGuests
        },
        start_date: new Date(formData.checkInDate).toISOString(),
        end_date: new Date(formData.checkOutDate).toISOString(),
        total_amount: calculateTotal(),
        currency: 'NGN',
        user_id: selectedUser.id
      };

      await apiService.createBooking(bookingPayload);
      
      toast({
        title: "Success",
        description: "Hotel booking created successfully"
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
    setSelectedHotel(null);
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      checkInDate: '',
      checkOutDate: '',
      numberOfGuests: 1,
      specialRequests: ''
    });
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Hotel className="h-5 w-5" />
            Add Hotel Booking
          </DialogTitle>
          <DialogDescription>
            Create a new hotel booking for a user
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Loading State */}
          {(loadingUsers || loadingHotels) && (
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
                  <Command>
                    <CommandInput placeholder="Search users..." />
                    <CommandEmpty>No users found.</CommandEmpty>
                    <CommandGroup className="max-h-48 overflow-y-auto">
                      {users && users.length > 0 ? users.map((user) => (
                        <CommandItem
                          key={user?.id || Math.random()}
                          value={`${user?.first_name || ''} ${user?.last_name || ''} ${user?.email || ''}`}
                          onSelect={() => handleUserSelect(user)}
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              selectedUser?.id === user?.id ? "opacity-100" : "opacity-0"
                            )}
                          />
                          {user?.first_name || ''} {user?.last_name || ''} ({user?.email || ''})
                        </CommandItem>
                      )) : (
                        <div className="p-2 text-sm text-gray-500">No users available</div>
                      )}
                    </CommandGroup>
                  </Command>
                )}
              </PopoverContent>
            </Popover>
          </div>

          {/* Hotel Selection */}
          <div className="space-y-2">
            <Label>Select Hotel *</Label>
            <Popover open={hotelSearchOpen} onOpenChange={setHotelSearchOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={hotelSearchOpen}
                  className="w-full justify-between"
                >
                  {selectedHotel ? `${selectedHotel.name || 'Unknown Hotel'} - ₦${(selectedHotel.price_per_night || 0).toLocaleString()}/night` : "Search hotels..."}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                {loadingHotels ? (
                  <div className="p-4 text-center text-sm text-gray-600">Loading hotels...</div>
                ) : (
                  <Command>
                    <CommandInput placeholder="Search hotels..." />
                    <CommandEmpty>No hotels found.</CommandEmpty>
                    <CommandGroup className="max-h-48 overflow-y-auto">
                      {hotels && hotels.length > 0 ? hotels.map((hotel) => (
                        <CommandItem
                          key={hotel?.id || Math.random()}
                          value={`${hotel?.name || 'Unknown Hotel'}`}
                          onSelect={() => handleHotelSelect(hotel)}
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              selectedHotel?.id === hotel?.id ? "opacity-100" : "opacity-0"
                            )}
                          />
                          {hotel?.name || 'Unknown Hotel'} - ₦{(hotel?.price_per_night || 0).toLocaleString()}/night
                        </CommandItem>
                      )) : (
                        <div className="p-2 text-sm text-gray-500">No hotels available</div>
                      )}
                    </CommandGroup>
                  </Command>
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

          {/* Booking Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="checkInDate">Check-in Date *</Label>
              <Input
                id="checkInDate"
                type="date"
                value={formData.checkInDate}
                onChange={(e) => setFormData(prev => ({ ...prev, checkInDate: e.target.value }))}
              />
            </div>
            <div>
              <Label htmlFor="checkOutDate">Check-out Date *</Label>
              <Input
                id="checkOutDate"
                type="date"
                value={formData.checkOutDate}
                onChange={(e) => setFormData(prev => ({ ...prev, checkOutDate: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="numberOfGuests">Number of Guests</Label>
            <Select value={formData.numberOfGuests.toString()} onValueChange={(value) => setFormData(prev => ({ ...prev, numberOfGuests: parseInt(value) }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[1,2,3,4,5,6,7,8].map(num => (
                  <SelectItem key={num} value={num.toString()}>{num} Guest{num > 1 ? 's' : ''}</SelectItem>
                ))}
              </SelectContent>
            </Select>
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
          {selectedHotel && formData.checkInDate && formData.checkOutDate && calculateTotal() > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Booking Summary</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Hotel:</span>
                  <span>{selectedHotel.name || 'Unknown Hotel'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Price per night:</span>
                  <span>₦{(selectedHotel.price_per_night || 0).toLocaleString()}</span>
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

export default AddHotelBookingModal;