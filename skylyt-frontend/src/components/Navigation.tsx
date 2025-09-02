
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Car, Hotel, User, Menu, X, LogOut, Settings, Bell, ChevronDown } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSettings } from '@/contexts/SettingsContext';
import { useNotifications } from '@/contexts/NotificationContext';
import { useFeatures } from '@/contexts/FeaturesContext';
import CurrencySelector from './CurrencySelector';

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, logout, isAuthenticated, hasRole } = useAuth();
  const { settings } = useSettings();
  const { notifications, unreadCount, markAsRead } = useNotifications();
  const { features } = useFeatures();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-teal-600 rounded-lg flex items-center justify-center">
              <Car className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-800">{settings?.site_name || 'Skylyt Luxury'}</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-600 hover:text-blue-600 transition-colors">
              Home
            </Link>
            {features.car_rental_enabled && (
              <Link to="/cars" className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors">
                <Car className="h-4 w-4" />
                <span>Cars</span>
              </Link>
            )}
            {features.hotel_booking_enabled && (
              <Link to="/hotels" className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors">
                <Hotel className="h-4 w-4" />
                <span>Hotels</span>
              </Link>
            )}
            <Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">
              About
            </Link>
            <Link to="/contact" className="text-gray-600 hover:text-blue-600 transition-colors">
              Contact
            </Link>
          </div>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <CurrencySelector />
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {/* Notifications */}
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="ghost" size="sm" className="relative">
                      <Bell className="h-4 w-4" />
                      {unreadCount > 0 && (
                        <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs">
                          {unreadCount}
                        </Badge>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80">
                    <div className="space-y-2">
                      <h4 className="font-medium">Notifications</h4>
                      {!notifications || notifications.length === 0 ? (
                        <p className="text-sm text-gray-500">No notifications</p>
                      ) : (
                        (notifications || []).slice(0, 5).map((notification) => (
                          <div
                            key={notification.id}
                            className={`p-2 rounded cursor-pointer ${
                              notification.read ? 'bg-gray-50' : 'bg-blue-50'
                            }`}
                            onClick={() => markAsRead(notification.id)}
                          >
                            <p className="text-sm font-medium">{notification.title}</p>
                            <p className="text-xs text-gray-600">{notification.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </PopoverContent>
                </Popover>
                
                {/* Profile Dropdown */}
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="ghost" className="flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-teal-600 text-white hover:from-blue-700 hover:to-teal-700 rounded-full px-3 py-1">
                      <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-xs font-medium">
                        {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
                      </div>
                      <ChevronDown className="h-3 w-3" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-48" align="end">
                    <div className="space-y-2">
                      <div className="px-2 py-1.5 text-sm font-medium">{user?.full_name}</div>
                      <div className="border-t pt-2 space-y-1">
                        {(hasRole('admin') || hasRole('superadmin')) && (
                          <Link to="/admin">
                            <Button variant="ghost" className="w-full justify-start">
                              <Settings className="h-4 w-4 mr-2" />
                              Admin Dashboard
                            </Button>
                          </Link>
                        )}
                        {hasRole('driver') && (
                          <Link to="/driver-dashboard">
                            <Button variant="ghost" className="w-full justify-start">
                              <Car className="h-4 w-4 mr-2" />
                              Driver Dashboard
                            </Button>
                          </Link>
                        )}
                        <Link to="/dashboard">
                          <Button variant="ghost" className="w-full justify-start">
                            <User className="h-4 w-4 mr-2" />
                            Dashboard
                          </Button>
                        </Link>
                      </div>
                      <div className="border-t pt-2">
                        <Button 
                          onClick={handleLogout} 
                          variant="ghost" 
                          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <LogOut className="h-4 w-4 mr-2" />
                          Logout
                        </Button>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              </div>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
                    Login
                  </Button>
                </Link>
                <Link to="/register">
                  <Button className="bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                    Register
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button and Profile */}
          <div className="md:hidden flex items-center space-x-3">
            {isAuthenticated && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white flex items-center justify-center text-sm font-medium">
                {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
              </div>
            )}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

      {/* Mobile Sidebar Overlay */}
      {isMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsMenuOpen(false)} />
          <div className="fixed right-0 top-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out">
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-end p-4 border-b">
                <button onClick={() => setIsMenuOpen(false)}>
                  <X className="h-6 w-6" />
                </button>
              </div>
              <div className="flex-1 p-4 space-y-4">
                <Link to="/" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                  <span>Home</span>
                </Link>
                {features.car_rental_enabled && (
                  <Link to="/cars" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                    <Car className="h-4 w-4" />
                    <span>Cars</span>
                  </Link>
                )}
                {features.hotel_booking_enabled && (
                  <Link to="/hotels" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                    <Hotel className="h-4 w-4" />
                    <span>Hotels</span>
                  </Link>
                )}
                <Link to="/about" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                  <span>About</span>
                </Link>
                <Link to="/contact" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                  <span>Contact</span>
                </Link>
                {isAuthenticated && (
                  <>
                    <div className="border-t pt-2 mt-4">
                      <p className="text-xs text-gray-500 mb-2 px-2">Account</p>
                      <Link to="/dashboard" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                        <User className="h-4 w-4" />
                        <span>Dashboard</span>
                      </Link>
                      {(hasRole('admin') || hasRole('superadmin')) && (
                        <Link to="/admin" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                          <Settings className="h-4 w-4" />
                          <span>Admin Dashboard</span>
                        </Link>
                      )}
                      {hasRole('driver') && (
                        <Link to="/driver-dashboard" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 py-2" onClick={() => setIsMenuOpen(false)}>
                          <Car className="h-4 w-4" />
                          <span>Driver Dashboard</span>
                        </Link>
                      )}
                    </div>
                  </>
                )}
              </div>
              <div className="p-4 border-t">
                {isAuthenticated ? (
                  <Button onClick={handleLogout} variant="outline" className="w-full flex items-center space-x-1 text-red-600 hover:text-red-700">
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <Link to="/login" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" className="text-blue-600 w-full">
                        Login
                      </Button>
                    </Link>
                    <Link to="/register" onClick={() => setIsMenuOpen(false)}>
                      <Button className="bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 w-full">
                        Register
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </nav>
  );
};

export default Navigation;
