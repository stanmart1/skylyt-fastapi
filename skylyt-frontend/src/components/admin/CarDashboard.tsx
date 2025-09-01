import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Car, BarChart3, Calendar, CreditCard, Settings, MessageSquare, ArrowLeft } from 'lucide-react';
import { CarManagement } from './CarManagement';
import CarBookingManagement from './CarBookingManagement';
import { PaymentManagement } from './PaymentManagement';
import { ReviewManagement } from './ReviewManagement';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';

interface CarDashboardProps {
  onBack: () => void;
}

export const CarDashboard = ({ onBack }: CarDashboardProps) => {
  const [activeTab, setActiveTab] = useState('analytics');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Overview
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-2">
              <Car className="h-8 w-8" />
              <span>Car Management Dashboard</span>
            </h1>
            <p className="text-gray-600">Comprehensive car rental business management</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Car Analytics</span>
          </TabsTrigger>
          <TabsTrigger value="bookings" className="flex items-center space-x-2">
            <Calendar className="h-4 w-4" />
            <span>Car Bookings</span>
          </TabsTrigger>
          <TabsTrigger value="payments" className="flex items-center space-x-2">
            <CreditCard className="h-4 w-4" />
            <span>Car Payment</span>
          </TabsTrigger>
          <TabsTrigger value="management" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Car Management</span>
          </TabsTrigger>
          <TabsTrigger value="reviews" className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4" />
            <span>Car Reviews</span>
          </TabsTrigger>
        </TabsList>

        {/* Car Analytics */}
        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Car Fleet Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <AnalyticsDashboard />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Car Bookings */}
        <TabsContent value="bookings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Car Rental Bookings</CardTitle>
            </CardHeader>
            <CardContent>
              <CarBookingManagement />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Car Payment */}
        <TabsContent value="payments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Car Rental Payments</CardTitle>
            </CardHeader>
            <CardContent>
              <PaymentManagement />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Car Management */}
        <TabsContent value="management" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fleet Management</CardTitle>
            </CardHeader>
            <CardContent>
              <CarManagement />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Car Reviews */}
        <TabsContent value="reviews" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Car Reviews & Feedback</CardTitle>
            </CardHeader>
            <CardContent>
              <ReviewManagement />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};