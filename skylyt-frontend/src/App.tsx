
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { SettingsProvider } from "./contexts/SettingsContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import { PaymentProvider } from "./contexts/PaymentContext";
import { CurrencyProvider } from "./contexts/CurrencyContext";
import { FeaturesProvider } from "./contexts/FeaturesContext";
import { MaintenanceMode } from "./components/MaintenanceMode";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ProtectedRoute } from "./components/ProtectedRoute";
import LoadingSpinner from "./components/LoadingSpinner";
import { usePageTransition } from "./hooks/usePageTransition";
import { Suspense } from "react";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import { lazy } from "react";

// Lazy load heavy admin components
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const DriverDashboard = lazy(() => import("./pages/DriverDashboard"));
const HotelBookingsPage = lazy(() => import("./pages/HotelBookingsPage"));
const CarBookingsPage = lazy(() => import("./pages/CarBookingsPage"));
const FleetManagement = lazy(() => import("./pages/FleetManagement"));
const HotelManagement = lazy(() => import("./pages/HotelManagement"));
const CarManagement = lazy(() => import("./pages/CarManagement"));

// Keep critical path components as regular imports
import Cars from "./pages/Cars";
import Hotels from "./pages/Hotels";
import HotelDetail from "./pages/HotelDetail";
import CarDetail from "./pages/CarDetail";
import Booking from "./pages/Booking";
import Payment from "./pages/Payment";
import PaymentConfirmation from "./pages/PaymentConfirmation";
import BookingDetails from "./pages/BookingDetails";

import Destinations from "./pages/Destinations";
import StateDestinationPage from "./pages/StateDestinationPage";
import CityHotelsPage from "./pages/CityHotelsPage";
import TermsOfService from "./pages/TermsOfService";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import Contact from "./pages/Contact";
import About from "./pages/About";

import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <SettingsProvider>
            <FeaturesProvider>
              <NotificationProvider>
                <PaymentProvider>
                  <CurrencyProvider>
                    <TooltipProvider>
              <Toaster />
              <Sonner />
              <BrowserRouter>
                <PageTransitionWrapper />
              </BrowserRouter>
                    </TooltipProvider>
                  </CurrencyProvider>
                </PaymentProvider>
              </NotificationProvider>
            </FeaturesProvider>
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
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password" element={<ResetPassword />} />
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
                <Route path="/driver-dashboard" element={
                  <ProtectedRoute requireRole="driver">
                    <DriverDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/cars" element={<Cars />} />
                <Route path="/hotels" element={<Hotels />} />
                <Route path="/hotel/:id" element={<HotelDetail />} />
                <Route path="/car/:id" element={<CarDetail />} />
                <Route path="/booking" element={<Booking />} />
                <Route path="/payment" element={<Payment />} />
                <Route path="/payment-confirmation" element={<PaymentConfirmation />} />
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
                <Route path="/admin/hotel-bookings" element={
                  <ProtectedRoute requireAdmin>
                    <HotelBookingsPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/car-bookings" element={
                  <ProtectedRoute requireAdmin>
                    <CarBookingsPage />
                  </ProtectedRoute>
                } />

                <Route path="/destinations" element={<Destinations />} />
                <Route path="/destinations/:stateSlug" element={<StateDestinationPage />} />
                <Route path="/destinations/:stateSlug/:citySlug" element={<CityHotelsPage />} />
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/about" element={<About />} />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </MaintenanceMode>
      </>
    );
  };

export default App;
