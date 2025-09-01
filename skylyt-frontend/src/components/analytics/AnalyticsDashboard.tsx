import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from 'lucide-react';
import { apiService } from '@/services/api';

interface RecentActivity {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  status?: string;
}

export const AnalyticsDashboard = () => {
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        const response = await apiService.request('/admin/recent-activity');
        setActivities(response.activities || []);
      } catch (error) {
        console.error('Failed to fetch recent activity:', error);
        setActivities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentActivity();
  }, []);

  if (loading) {
    return <div className="flex justify-center p-8">Loading recent activity...</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5" />
            <span>Recent Activity</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activities.length > 0 ? (
              activities.map((activity) => (
                <div key={activity.id} className="flex justify-between items-start p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{activity.title || activity.description}</p>
                    <p className="text-sm text-gray-600">{activity.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    activity.type === 'user' ? 'bg-blue-100 text-blue-800' :
                    activity.type === 'booking' ? 'bg-green-100 text-green-800' :
                    activity.type === 'payment' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {activity.type}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No recent activity found</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};