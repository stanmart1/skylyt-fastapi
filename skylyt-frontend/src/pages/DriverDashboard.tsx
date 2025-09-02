import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Car, 
  User, 
  Calendar, 
  MapPin, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Star,
  Phone,
  Mail,
  Edit,
  Navigation,
  TrendingUp,
  DollarSign
} from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import Navigation from '@/components/Navigation';

interface DriverProfile {
  id: number;
  name: string;
  email: string;
  phone: string;
  license_number: string;
  license_expiry?: string;
  license_class?: string;
  is_available: boolean;
  is_active: boolean;
  rating: number;
  total_trips: number;
  address?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  notes?: string;
}

interface Trip {
  id: number;
  booking_reference: string;
  booking_type: string;
  status: string;
  trip_status: string;
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
  start_date: string;
  end_date: string;
  pickup_location?: string;
  dropoff_location?: string;
  special_requests?: string;
  total_amount: number;
  currency: string;
  created_at: string;
}

const DriverDashboard = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [driverProfile, setDriverProfile] = useState<DriverProfile | null>(null);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [tripsLoading, setTripsLoading] = useState(false);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({
    phone: '',
    address: '',
    emergency_contact: '',
    emergency_phone: '',
    notes: ''
  });

  useEffect(() => {
    fetchDriverProfile();
    fetchMyTrips();
  }, []);

  const fetchDriverProfile = async () => {
    try {
      const data = await apiService.request('/driver/profile');
      setDriverProfile(data);
      setProfileForm({
        phone: data.phone || '',
        address: data.address || '',
        emergency_contact: data.emergency_contact || '',
        emergency_phone: data.emergency_phone || '',
        notes: data.notes || ''
      });
    } catch (error) {
      console.error('Failed to fetch driver profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to load driver profile',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchMyTrips = async () => {
    setTripsLoading(true);
    try {
      const data = await apiService.request('/driver/trips');
      setTrips(data.trips || []);
    } catch (error) {
      console.error('Failed to fetch trips:', error);
      toast({
        title: 'Error',
        description: 'Failed to load trips',
        variant: 'destructive'
      });
    } finally {
      setTripsLoading(false);
    }
  };

  const handleToggleAvailability = async () => {
    if (!driverProfile) return;
    
    try {
      await apiService.request('/driver/availability', {
        method: 'PUT',
        body: JSON.stringify({ is_available: !driverProfile.is_available })
      });
      
      setDriverProfile({
        ...driverProfile,
        is_available: !driverProfile.is_available
      });
      
      toast({
        title: 'Success',
        description: `You are now ${!driverProfile.is_available ? 'available' : 'busy'}`,
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update availability:', error);
      toast({
        title: 'Error',
        description: 'Failed to update availability',
        variant: 'destructive'
      });
    }
  };

  const handleUpdateProfile = async () => {
    try {
      await apiService.request('/driver/profile', {
        method: 'PUT',
        body: JSON.stringify(profileForm)
      });
      
      await fetchDriverProfile();
      setIsEditProfileOpen(false);
      
      toast({
        title: 'Success',
        description: 'Profile updated successfully',
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to update profile',
        variant: 'destructive'
      });
    }
  };

  const handleUpdateTripStatus = async (tripId: number, newStatus: string) => {
    try {
      await apiService.request(`/driver/trips/${tripId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ trip_status: newStatus })
      });
      
      await fetchMyTrips();
      
      toast({
        title: 'Success',
        description: 'Trip status updated successfully',
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update trip status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update trip status',
        variant: 'destructive'
      });
    }
  };

  const getTripStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-gray-100 text-gray-800';
      case 'en_route': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTripStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'en_route': return 'En Route';
      case 'in_progress': return 'In Progress';
      case 'completed': return 'Completed';
      case 'cancelled': return 'Cancelled';
      default: return 'Unknown';
    }
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="space-y-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse h-32 bg-gray-200 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Driver Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back, {driverProfile?.name}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Driver Profile Card */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    My Profile
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditProfileOpen(true)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {driverProfile && (
                  <>
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-teal-600 rounded-full flex items-center justify-center text-white text-xl font-bold mx-auto mb-3">
                        {driverProfile.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                      </div>
                      <h3 className="font-semibold text-lg">{driverProfile.name}</h3>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        {renderStars(Math.round(driverProfile.rating))}
                        <span className="text-sm text-gray-600 ml-1">({driverProfile.rating.toFixed(1)})</span>
                      </div>
                    </div>

                    <div className="space-y-3 text-sm">
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-gray-500" />
                        <span>{driverProfile.email}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-gray-500" />
                        <span>{driverProfile.phone}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <span>License: {driverProfile.license_number}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t">
                      <span className="text-sm font-medium">Availability</span>
                      <Button
                        onClick={handleToggleAvailability}
                        variant={driverProfile.is_available ? "default" : "outline"}
                        size="sm"
                      >
                        {driverProfile.is_available ? (
                          <>
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Available
                          </>
                        ) : (
                          <>
                            <Clock className="h-4 w-4 mr-1" />
                            Busy
                          </>
                        )}
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Stats Card */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  My Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                {driverProfile && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{driverProfile.total_trips}</div>
                      <div className="text-sm text-gray-600">Total Trips</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{driverProfile.rating.toFixed(1)}</div>
                      <div className="text-sm text-gray-600">Rating</div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Trips Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Car className="h-5 w-5" />
                  My Trips
                </CardTitle>
              </CardHeader>
              <CardContent>
                {tripsLoading ? (
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="animate-pulse h-24 bg-gray-200 rounded" />
                    ))}
                  </div>
                ) : trips.length === 0 ? (
                  <div className="text-center py-8">
                    <Car className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No trips assigned yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {trips.map((trip) => (
                      <div key={trip.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-semibold">{trip.booking_reference}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge className={getTripStatusColor(trip.trip_status)}>
                                {getTripStatusText(trip.trip_status)}
                              </Badge>
                              <Badge variant="outline">{trip.booking_type}</Badge>
                            </div>
                          </div>
                          {trip.trip_status !== 'completed' && trip.trip_status !== 'cancelled' && (
                            <Select
                              value={trip.trip_status}
                              onValueChange={(value) => handleUpdateTripStatus(trip.id, value)}
                            >
                              <SelectTrigger className="w-40">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="pending">Pending</SelectItem>
                                <SelectItem value="en_route">En Route</SelectItem>
                                <SelectItem value="in_progress">In Progress</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                              </SelectContent>
                            </Select>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="font-medium text-gray-700">Customer</p>
                            <p>{trip.customer_name}</p>
                            <p className="text-gray-600">{trip.customer_email}</p>
                            {trip.customer_phone && <p className="text-gray-600">{trip.customer_phone}</p>}
                          </div>
                          
                          <div>
                            <p className="font-medium text-gray-700">Trip Details</p>
                            <p>Start: {new Date(trip.start_date).toLocaleString()}</p>
                            <p>End: {new Date(trip.end_date).toLocaleString()}</p>
                            <p className="font-medium text-green-600">${trip.total_amount} {trip.currency}</p>
                          </div>
                        </div>
                        
                        {(trip.pickup_location || trip.dropoff_location) && (
                          <div className="mt-3 flex items-center gap-4 text-sm">
                            {trip.pickup_location && (
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3 text-blue-500" />
                                <span>{trip.pickup_location}</span>
                              </div>
                            )}
                            {trip.dropoff_location && (
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3 text-red-500" />
                                <span>→ {trip.dropoff_location}</span>
                              </div>
                            )}
                          </div>
                        )}
                        
                        {trip.special_requests && (
                          <div className="mt-3 p-2 bg-yellow-50 rounded">
                            <p className="text-sm font-medium text-gray-700">Special Requests:</p>
                            <p className="text-sm text-gray-600">{trip.special_requests}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Edit Profile Modal */}
        <Dialog open={isEditProfileOpen} onOpenChange={setIsEditProfileOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Edit Profile</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                  placeholder="Enter phone number"
                />
              </div>
              <div>
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={profileForm.address}
                  onChange={(e) => setProfileForm({ ...profileForm, address: e.target.value })}
                  placeholder="Enter address"
                />
              </div>
              <div>
                <Label htmlFor="emergency_contact">Emergency Contact</Label>
                <Input
                  id="emergency_contact"
                  value={profileForm.emergency_contact}
                  onChange={(e) => setProfileForm({ ...profileForm, emergency_contact: e.target.value })}
                  placeholder="Emergency contact name"
                />
              </div>
              <div>
                <Label htmlFor="emergency_phone">Emergency Phone</Label>
                <Input
                  id="emergency_phone"
                  value={profileForm.emergency_phone}
                  onChange={(e) => setProfileForm({ ...profileForm, emergency_phone: e.target.value })}
                  placeholder="Emergency contact phone"
                />
              </div>
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={profileForm.notes}
                  onChange={(e) => setProfileForm({ ...profileForm, notes: e.target.value })}
                  placeholder="Additional notes"
                  rows={3}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button onClick={handleUpdateProfile} className="flex-1">
                  Update Profile
                </Button>
                <Button variant="outline" onClick={() => setIsEditProfileOpen(false)}>
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

export default DriverDashboard;