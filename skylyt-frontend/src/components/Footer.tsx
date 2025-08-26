
import { Link } from 'react-router-dom';
import { Car, Phone, Mail, MapPin, Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-teal-600 rounded-lg flex items-center justify-center">
                <Car className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Skylyt Luxury</span>
            </div>
            <p className="text-gray-400">
              Your perfect journey awaits. Rent premium cars and book luxurious hotels with confidence.
            </p>
            <div className="flex space-x-4">
              <Twitter className="h-5 w-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
              <Instagram className="h-5 w-5 text-gray-400 hover:text-pink-500 cursor-pointer transition-colors" />
              <Linkedin className="h-5 w-5 text-gray-400 hover:text-blue-600 cursor-pointer transition-colors" />
            </div>
          </div>

          {/* Support */}
          <div className="space-y-4 ml-8">
            <h3 className="text-lg font-semibold">Support</h3>
            <div className="space-y-2">
              <Link to="/help" className="block text-gray-400 hover:text-white transition-colors">
                Help Center
              </Link>
              <Link to="/contact" className="block text-gray-400 hover:text-white transition-colors">
                Contact Us
              </Link>
              <Link to="/faq" className="block text-gray-400 hover:text-white transition-colors">
                FAQ
              </Link>
              <Link to="/terms" className="block text-gray-400 hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link to="/privacy" className="block text-gray-400 hover:text-white transition-colors">
                Privacy Policy
              </Link>
            </div>
          </div>

          {/* Empty column for spacing */}
          <div></div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contact Info</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <MapPin className="h-5 w-5 text-gray-400" />
                <span className="text-gray-400">123 Business Ave, Suite 100<br />New York, NY 10001</span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="h-5 w-5 text-gray-400" />
                <span className="text-gray-400">+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-3">
                <Mail className="h-5 w-5 text-gray-400" />
                <span className="text-gray-400">support@skylytluxury.com</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 relative flex justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2025 Skylyt Luxury. All rights reserved.
          </p>
          <p className="text-gray-400 text-sm flex items-center absolute left-1/2 transform -translate-x-1/2">
            Built With <span className="text-red-500 mx-1 animate-bounce" style={{animationDuration: '1s'}}>❤️</span> by Scaleitpro
          </p>
          <div className="flex space-x-6">
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
