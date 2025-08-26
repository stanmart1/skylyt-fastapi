
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { SettingsProvider } from "./contexts/SettingsContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import { PaymentProvider } from "./contexts/PaymentContext";
import { MaintenanceMode } from "./components/MaintenanceMode";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ProtectedRoute } from "./components/ProtectedRoute";
import LoadingSpinner from "./components/LoadingSpinner";
import { usePageTransition } from "./hooks/usePageTransition";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Cars from "./pages/Cars";
import Hotels from "./pages/Hotels";
import HotelDetail from "./pages/HotelDetail";
import CarDetail from "./pages/CarDetail";
import Booking from "./pages/Booking";
import Payment from "./pages/Payment";
import BookingDetails from "./pages/BookingDetails";
import FleetManagement from "./pages/FleetManagement";
import HotelManagement from "./pages/HotelManagement";
import CarManagement from "./pages/CarManagement";
import StateDestinationPage from "./pages/StateDestinationPage";
import CityHotelsPage from "./pages/CityHotelsPage";

import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <SettingsProvider>
            <NotificationProvider>
              <PaymentProvider>
                <TooltipProvider>
              <Toaster />
              <Sonner />
              <BrowserRouter>
                <PageTransitionWrapper />
              </BrowserRouter>
                </TooltipProvider>
              </PaymentProvider>
            </NotificationProvider>
          </SettingsProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

const PageTransitionWrapper = () => {
  const isLoading = usePageTransition();
  
  return (
    <>
      {isLoading && <LoadingSpinner />}
      <MaintenanceMode>
        <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } />
                <Route path="/admin" element={
                  <ProtectedRoute requireAdmin>
                    <AdminDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/cars" element={<Cars />} />
                <Route path="/hotels" element={<Hotels />} />
                <Route path="/hotel/:id" element={<HotelDetail />} />
                <Route path="/car/:id" element={<CarDetail />} />
                <Route path="/booking" element={<Booking />} />
                <Route path="/payment" element={<Payment />} />
                <Route path="/booking/:id" element={
                  <ProtectedRoute>
                    <BookingDetails />
                  </ProtectedRoute>
                } />
                <Route path="/admin/fleet" element={
                  <ProtectedRoute requireAdmin>
                    <FleetManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/hotels" element={
                  <ProtectedRoute requireAdmin>
                    <HotelManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/cars" element={
                  <ProtectedRoute requireAdmin>
                    <CarManagement />
                  </ProtectedRoute>
                } />
                <Route path="/destinations/:stateSlug" element={<StateDestinationPage />} />
                <Route path="/destinations/:stateSlug/:citySlug" element={<CityHotelsPage />} />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
          </Routes>
        </MaintenanceMode>
      </>
    );
  };

export default App;
