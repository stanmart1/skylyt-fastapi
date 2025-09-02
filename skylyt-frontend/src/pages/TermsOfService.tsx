import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
          <p className="text-gray-600 mb-8">Last updated: January 2025</p>

          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                By accessing and using Skylyt Luxury's services, you accept and agree to be bound by the terms and provision of this agreement. 
                If you do not agree to abide by the above, please do not use this service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Booking and Reservations</h2>
              <div className="space-y-4 text-gray-700">
                <p>• All bookings are subject to availability and confirmation.</p>
                <p>• Payment is required at the time of booking to secure your reservation.</p>
                <p>• Booking confirmations will be sent via email within 24 hours.</p>
                <p>• Special requests are subject to availability and may incur additional charges.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Cancellation Policy</h2>
              <div className="space-y-4 text-gray-700">
                <p><strong>Car Rentals:</strong></p>
                <p>• Free cancellation up to 24 hours before pickup time.</p>
                <p>• Cancellations within 24 hours may incur a 50% charge.</p>
                <p><strong>Hotel Bookings:</strong></p>
                <p>• Free cancellation up to 48 hours before check-in.</p>
                <p>• Late cancellations may incur charges as per hotel policy.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Payment Terms</h2>
              <div className="space-y-4 text-gray-700">
                <p>• We accept major credit cards, PayPal, and local payment methods.</p>
                <p>• All prices are inclusive of applicable taxes unless stated otherwise.</p>
                <p>• Currency conversion rates are applied at the time of booking.</p>
                <p>• Refunds will be processed within 5-10 business days.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. User Responsibilities</h2>
              <div className="space-y-4 text-gray-700">
                <p>• Provide accurate and complete information during booking.</p>
                <p>• Present valid identification and required documents.</p>
                <p>• Comply with all applicable laws and regulations.</p>
                <p>• Report any damages or issues immediately.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Limitation of Liability</h2>
              <p className="text-gray-700 leading-relaxed">
                Skylyt Luxury acts as an intermediary between customers and service providers. We are not liable for any 
                direct, indirect, incidental, or consequential damages arising from the use of our services or third-party providers.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Privacy and Data Protection</h2>
              <p className="text-gray-700 leading-relaxed">
                Your privacy is important to us. Please review our Privacy Policy to understand how we collect, 
                use, and protect your personal information.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Changes to Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                We reserve the right to modify these terms at any time. Changes will be effective immediately upon 
                posting on our website. Continued use of our services constitutes acceptance of modified terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed">
                If you have any questions about these Terms of Service, please contact us at:
                <br />
                Email: support@skylytluxury.com
                <br />
                Phone: +1 (555) 123-4567
              </p>
            </section>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default TermsOfService;