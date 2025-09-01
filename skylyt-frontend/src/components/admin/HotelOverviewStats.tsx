import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2, Bed, Calendar, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiService } from '@/services/api';

interface HotelStatus {
  total_hotels: number;
  total_rooms: number;
  available_rooms: number;
  occupied_rooms: number;
}

interface BookingStatus {
  pending: number;
  confirmed: number;
  cancelled: number;
}

interface BookingTrend {
  date: string;
  bookings: number;
}

interface HotelOverviewStats {
  hotel_status: HotelStatus;
  booking_status: BookingStatus;
  booking_trends: BookingTrend[];
}

export const HotelOverviewStats = () => {
  const [stats, setStats] = useState<HotelOverviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDays, setSelectedDays] = useState(7);

  const fetchHotelStats = async (days: number = 7) => {
    try {
      setLoading(true);
      const response = await apiService.request(`/admin/hotels/overview-stats?days=${days}`);
      setStats(response);
    } catch (error) {
      console.error('Failed to fetch hotel overview stats:', error);
      setStats({
        hotel_status: {
          total_hotels: 0,
          total_rooms: 0,
          available_rooms: 0,
          occupied_rooms: 0
        },
        booking_status: {
          pending: 0,
          confirmed: 0,
          cancelled: 0
        },
        booking_trends: []
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHotelStats(selectedDays);
  }, [selectedDays]);

  const handleDaysChange = (days: number) => {
    setSelectedDays(days);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4 sm:p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded mb-2" />
                  <div className="h-8 bg-gray-200 rounded mb-1" />
                  <div className="h-3 bg-gray-200 rounded w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4 sm:p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded mb-4" />
                  <div className="h-48 bg-gray-200 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-4">Hotel Status Summary</h2>
      </div>
      
      {/* Hotel Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Hotels</CardTitle>
            <Building2 className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.hotel_status?.total_hotels || 0}</div>
            <p className="text-xs text-blue-100">Hotels on platform</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Rooms</CardTitle>
            <Bed className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.hotel_status?.total_rooms || 0}</div>
            <p className="text-xs text-green-100">Available inventory</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Available Rooms</CardTitle>
            <Bed className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.hotel_status?.available_rooms || 0}</div>
            <p className="text-xs text-yellow-100">Ready to book</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Occupied Rooms</CardTitle>
            <Calendar className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.hotel_status?.occupied_rooms || 0}</div>
            <p className="text-xs text-purple-100">Currently booked</p>
          </CardContent>
        </Card>
      </div>

      {/* Booking Status Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-orange-800">Pending Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-800">{stats?.booking_status?.pending || 0}</div>
            <p className="text-xs text-orange-600">Awaiting confirmation</p>
          </CardContent>
        </Card>

        <Card className="border-green-200 bg-green-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-green-800">Confirmed Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-800">{stats?.booking_status?.confirmed || 0}</div>
            <p className="text-xs text-green-600">Active reservations</p>
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-800">Cancelled Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-800">{stats?.booking_status?.cancelled || 0}</div>
            <p className="text-xs text-red-600">Cancelled reservations</p>
          </CardContent>
        </Card>
      </div>

      {/* Booking Trends Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Booking Trends</span>
            </CardTitle>
            <select 
              value={selectedDays} 
              onChange={(e) => handleDaysChange(Number(e.target.value))}
              className="px-3 py-1 border rounded-md text-sm bg-white"
            >
              <option value={7}>Last 7 Days</option>
              <option value={30}>Last 30 Days</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats?.booking_trends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  fontSize={12}
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }}
                />
                <YAxis 
                  fontSize={12}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString();
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="bookings" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={{ fill: '#8b5cf6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};