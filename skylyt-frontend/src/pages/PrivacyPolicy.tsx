import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';

const PrivacyPolicy = () => {
  const [contactInfo, setContactInfo] = useState({
    contact_email: '',
    contact_phone: '',
    contact_address: ''
  });

  useEffect(() => {
    const fetchContactInfo = async () => {
      try {
        const data = await apiService.request('/footer-settings');
        setContactInfo({
          contact_email: data.contact_email || 'privacy@skylytluxury.com',
          contact_phone: data.contact_phone || '+1 (555) 123-4567',
          contact_address: data.contact_address ? data.contact_address.replace('\n', ', ') : '123 Business Ave, Suite 100, New York, NY 10001'
        });
      } catch (error) {
        console.error('Failed to fetch contact info:', error);
        setContactInfo({
          contact_email: 'privacy@skylytluxury.com',
          contact_phone: '+1 (555) 123-4567',
          contact_address: '123 Business Ave, Suite 100, New York, NY 10001'
        });
      }
    };
    
    fetchContactInfo();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
          <p className="text-gray-600 mb-8">Last updated: January 2025</p>

          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Information We Collect</h2>
              <div className="space-y-4 text-gray-700">
                <p><strong>Personal Information:</strong></p>
                <p>• Name, email address, phone number</p>
                <p>• Billing and payment information</p>
                <p>• Government-issued ID for verification</p>
                <p>• Travel preferences and special requests</p>
                
                <p><strong>Automatically Collected Information:</strong></p>
                <p>• IP address and device information</p>
                <p>• Browser type and operating system</p>
                <p>• Usage patterns and website interactions</p>
                <p>• Location data (with your consent)</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. How We Use Your Information</h2>
              <div className="space-y-4 text-gray-700">
                <p>We use your information to:</p>
                <p>• Process bookings and provide travel services</p>
                <p>• Send booking confirmations and updates</p>
                <p>• Provide customer support and assistance</p>
                <p>• Improve our services and user experience</p>
                <p>• Send promotional offers (with your consent)</p>
                <p>• Comply with legal obligations</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Information Sharing</h2>
              <div className="space-y-4 text-gray-700">
                <p>We may share your information with:</p>
                <p>• <strong>Service Providers:</strong> Hotels, car rental companies, and payment processors</p>
                <p>• <strong>Business Partners:</strong> Trusted third parties who help us operate our services</p>
                <p>• <strong>Legal Requirements:</strong> When required by law or to protect our rights</p>
                <p>• <strong>Business Transfers:</strong> In case of merger, acquisition, or sale of assets</p>
                
                <p className="font-semibold">We never sell your personal information to third parties.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Data Security</h2>
              <p className="text-gray-700 leading-relaxed">
                We implement industry-standard security measures to protect your personal information, including:
                encryption, secure servers, regular security audits, and access controls. However, no method of 
                transmission over the internet is 100% secure.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Cookies and Tracking</h2>
              <div className="space-y-4 text-gray-700">
                <p>We use cookies and similar technologies to:</p>
                <p>• Remember your preferences and settings</p>
                <p>• Analyze website traffic and usage patterns</p>
                <p>• Provide personalized content and advertisements</p>
                <p>• Improve website functionality and performance</p>
                
                <p>You can control cookie settings through your browser preferences.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Your Rights</h2>
              <div className="space-y-4 text-gray-700">
                <p>You have the right to:</p>
                <p>• Access and review your personal information</p>
                <p>• Correct inaccurate or incomplete data</p>
                <p>• Delete your account and personal information</p>
                <p>• Opt-out of marketing communications</p>
                <p>• Data portability and transfer</p>
                <p>• Lodge complaints with data protection authorities</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Retention</h2>
              <p className="text-gray-700 leading-relaxed">
                We retain your personal information for as long as necessary to provide our services, 
                comply with legal obligations, resolve disputes, and enforce our agreements. 
                Booking records are typically retained for 7 years for tax and legal purposes.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. International Transfers</h2>
              <p className="text-gray-700 leading-relaxed">
                Your information may be transferred to and processed in countries other than your own. 
                We ensure appropriate safeguards are in place to protect your data in accordance with 
                applicable data protection laws.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed">
                Our services are not intended for children under 13 years of age. We do not knowingly 
                collect personal information from children under 13. If you believe we have collected 
                information from a child under 13, please contact us immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Changes to This Policy</h2>
              <p className="text-gray-700 leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any material 
                changes by posting the new policy on our website and updating the "Last updated" date. 
                Your continued use of our services constitutes acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Contact Us</h2>
              <div className="text-gray-700 leading-relaxed">
                <p>If you have any questions about this Privacy Policy or our data practices, please contact us:</p>
                <p className="mt-4">
                  <strong>Email:</strong> {contactInfo.contact_email}<br />
                  <strong>Phone:</strong> {contactInfo.contact_phone}<br />
                  <strong>Address:</strong> {contactInfo.contact_address}
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default PrivacyPolicy;