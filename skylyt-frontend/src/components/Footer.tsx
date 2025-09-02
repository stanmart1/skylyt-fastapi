
import { Link } from 'react-router-dom';
import { Car, Phone, Mail, MapPin, Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8 sm:py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* Company Info */}
          <div className="space-y-4 col-span-1 sm:col-span-2 lg:col-span-1">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-teal-600 rounded-lg flex items-center justify-center">
                <Car className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Skylyt Luxury</span>
            </div>
            <p className="text-gray-400 text-sm sm:text-base">
              Your perfect journey awaits. Rent premium cars and book luxurious hotels with confidence.
            </p>
            <div className="flex space-x-4">
              <Twitter className="h-5 w-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
              <Instagram className="h-5 w-5 text-gray-400 hover:text-pink-500 cursor-pointer transition-colors" />
              <Linkedin className="h-5 w-5 text-gray-400 hover:text-blue-600 cursor-pointer transition-colors" />
            </div>
          </div>

          {/* Support */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Support</h3>
            <div className="space-y-2">
              <Link to="/contact" className="block text-gray-400 hover:text-white transition-colors text-sm sm:text-base">
                Contact Us
              </Link>
              <Link to="/faq" className="block text-gray-400 hover:text-white transition-colors text-sm sm:text-base">
                FAQ
              </Link>
              <Link to="/terms" className="block text-gray-400 hover:text-white transition-colors text-sm sm:text-base">
                Terms of Service
              </Link>
              <Link to="/privacy" className="block text-gray-400 hover:text-white transition-colors text-sm sm:text-base">
                Privacy Policy
              </Link>
            </div>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contact Info</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <MapPin className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <span className="text-gray-400 text-sm sm:text-base leading-relaxed">
                  123 Business Ave, Suite 100<br />New York, NY 10001
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="h-5 w-5 text-gray-400 flex-shrink-0" />
                <span className="text-gray-400 text-sm sm:text-base">+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-3">
                <Mail className="h-5 w-5 text-gray-400 flex-shrink-0" />
                <span className="text-gray-400 text-sm sm:text-base break-all">support@skylytluxury.com</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-6 sm:mt-8 pt-6 sm:pt-8">
          <div className="flex flex-col items-center space-y-4 sm:flex-row sm:justify-between sm:space-y-0">
            <p className="text-gray-400 text-xs sm:text-sm text-center sm:text-left order-1 sm:order-1">
              © 2025 Skylyt Luxury. All rights reserved.
            </p>
            <p className="text-gray-400 text-xs sm:text-sm flex items-center justify-center order-2 sm:order-2">
              Built With <span className="text-red-500 mx-1 animate-pulse" style={{animationDuration: '1.5s'}}>❤️</span> by <a href="https://scaleitpro.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors ml-1">Scaleitpro</a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
