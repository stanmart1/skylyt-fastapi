import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Car, Wrench, AlertTriangle, TrendingUp, PieChart } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell, Pie } from 'recharts';
import { apiService } from '@/services/api';

interface FleetStatus {
  total_cars: number;
  available: number;
  rented: number;
  maintenance: number;
}

interface RentalTrend {
  month: string;
  rentals: number;
}

interface FleetDistribution {
  name: string;
  value: number;
  color: string;
}

interface MaintenanceAlert {
  car_name: string;
  type: string;
  due_date: string;
}

interface CarFleetStats {
  fleet_status: FleetStatus;
  rental_trends: RentalTrend[];
  fleet_distribution: FleetDistribution[];
  maintenance_alerts: MaintenanceAlert[];
}

export const CarFleetStats = () => {
  const [stats, setStats] = useState<CarFleetStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFleetStats = async () => {
      try {
        const response = await apiService.request('/admin/cars/fleet-stats');
        setStats(response);
      } catch (error) {
        console.error('Failed to fetch fleet stats:', error);
        setStats({
          fleet_status: {
            total_cars: 0,
            available: 0,
            rented: 0,
            maintenance: 0
          },
          rental_trends: [],
          fleet_distribution: [
            { name: 'Available', value: 0, color: '#10b981' },
            { name: 'Rented', value: 0, color: '#3b82f6' },
            { name: 'Maintenance', value: 0, color: '#f59e0b' }
          ],
          maintenance_alerts: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchFleetStats();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
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
              <CardContent className="p-6">
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
        <h2 className="text-xl font-semibold mb-4">Fleet Status Summary</h2>
      </div>
      
      {/* Fleet Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Fleet</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.fleet_status?.total_cars || 0}</div>
            <p className="text-xs text-blue-100">Cars in fleet</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Available</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.fleet_status?.available || 0}</div>
            <p className="text-xs text-green-100">Ready to rent</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Rented</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.fleet_status?.rented || 0}</div>
            <p className="text-xs text-yellow-100">Currently rented</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Maintenance</CardTitle>
            <Wrench className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.fleet_status?.maintenance || 0}</div>
            <p className="text-xs text-red-100">Under maintenance</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rental Trends Line Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Rental Trends</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats?.rental_trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="rentals" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Fleet Distribution Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="h-5 w-5" />
              <span>Fleet Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={stats?.fleet_distribution || []}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {stats?.fleet_distribution?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Maintenance Alerts */}
      {stats?.maintenance_alerts && stats.maintenance_alerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Maintenance Alerts</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.maintenance_alerts.map((alert, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-orange-100 rounded">
                  <div>
                    <p className="text-orange-800 font-medium">{alert.car_name}</p>
                    <p className="text-sm text-orange-600">{alert.type} - Due: {alert.due_date}</p>
                  </div>
                  <Badge className="bg-orange-200 text-orange-800">
                    Action Required
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};