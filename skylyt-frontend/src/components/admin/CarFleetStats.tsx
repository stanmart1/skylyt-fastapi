import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Car, Wrench, AlertTriangle } from 'lucide-react';
import { apiService } from '@/services/api';

interface CarFleetStats {
  total_cars: number;
  available: number;
  rented: number;
  maintenance: number;
  maintenance_due: number;
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
          total_cars: 0,
          available: 0,
          rented: 0,
          maintenance: 0,
          maintenance_due: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchFleetStats();
  }, []);

  if (loading) {
    return (
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
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-4">Fleet Status Summary</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Cars */}
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Fleet</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.total_cars || 0}</div>
            <p className="text-xs text-blue-100">Cars in fleet</p>
          </CardContent>
        </Card>

        {/* Available Cars */}
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Available</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.available || 0}</div>
            <p className="text-xs text-green-100">Ready to rent</p>
          </CardContent>
        </Card>

        {/* Rented Cars */}
        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Rented</CardTitle>
            <Car className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.rented || 0}</div>
            <p className="text-xs text-yellow-100">Currently rented</p>
          </CardContent>
        </Card>

        {/* Maintenance */}
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Maintenance</CardTitle>
            <Wrench className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.maintenance || 0}</div>
            <p className="text-xs text-red-100">Under maintenance</p>
          </CardContent>
        </Card>
      </div>

      {/* Maintenance Due Alert */}
      {stats && stats.maintenance_due > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Maintenance Alert</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-800 font-medium">
                  {stats.maintenance_due} car{stats.maintenance_due > 1 ? 's' : ''} due for maintenance/inspection
                </p>
                <p className="text-sm text-orange-600 mt-1">
                  Schedule maintenance to keep your fleet operational
                </p>
              </div>
              <Badge className="bg-orange-100 text-orange-800">
                Action Required
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};