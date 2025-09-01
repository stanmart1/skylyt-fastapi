import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { CreditCard, Save, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import Navigation from '@/components/Navigation';

export const PaymentSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { toast } = useToast();

  const [paymentForm, setPaymentForm] = useState({
    stripe_public_key: '',
    stripe_secret_key: '',
    paystack_public_key: '',
    paystack_secret_key: '',
    flutterwave_public_key: '',
    flutterwave_secret_key: '',
    paypal_client_id: '',
    paypal_client_secret: '',
    paypal_sandbox: true
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      setPaymentForm({
        stripe_public_key: data.stripe_public_key || '',
        stripe_secret_key: '',
        paystack_public_key: data.paystack_public_key || '',
        paystack_secret_key: '',
        flutterwave_public_key: data.flutterwave_public_key || '',
        flutterwave_secret_key: '',
        paypal_client_id: data.paypal_client_id || '',
        paypal_client_secret: '',
        paypal_sandbox: data.paypal_sandbox || true
      });
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      toast({
        title: "Error",
        description: "Failed to load settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const savePaymentSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/payment-gateway', {
        method: 'PUT',
        body: JSON.stringify(paymentForm)
      });
      
      toast({
        title: "Success",
        description: "Payment gateway settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update payment settings",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Payment Gateway Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!hasPermission('system.manage_settings')) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Payment Gateway Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Superadmin access required for payment gateway settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Payment Gateway Settings</h1>
          <p className="text-gray-600">Configure payment gateway integrations</p>
        </div>
        <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Payment Gateway Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Stripe</h3>
            <div>
              <Label htmlFor="stripe_public_key">Public Key</Label>
              <Input
                id="stripe_public_key"
                value={paymentForm.stripe_public_key}
                onChange={(e) => setPaymentForm({...paymentForm, stripe_public_key: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="stripe_secret_key">Secret Key</Label>
              <Input
                id="stripe_secret_key"
                type="password"
                value={paymentForm.stripe_secret_key}
                onChange={(e) => setPaymentForm({...paymentForm, stripe_secret_key: e.target.value})}
                placeholder="Enter to update"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Paystack</h3>
            <div>
              <Label htmlFor="paystack_public_key">Public Key</Label>
              <Input
                id="paystack_public_key"
                value={paymentForm.paystack_public_key}
                onChange={(e) => setPaymentForm({...paymentForm, paystack_public_key: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="paystack_secret_key">Secret Key</Label>
              <Input
                id="paystack_secret_key"
                type="password"
                value={paymentForm.paystack_secret_key}
                onChange={(e) => setPaymentForm({...paymentForm, paystack_secret_key: e.target.value})}
                placeholder="Enter to update"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Flutterwave</h3>
            <div>
              <Label htmlFor="flutterwave_public_key">Public Key</Label>
              <Input
                id="flutterwave_public_key"
                value={paymentForm.flutterwave_public_key}
                onChange={(e) => setPaymentForm({...paymentForm, flutterwave_public_key: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="flutterwave_secret_key">Secret Key</Label>
              <Input
                id="flutterwave_secret_key"
                type="password"
                value={paymentForm.flutterwave_secret_key}
                onChange={(e) => setPaymentForm({...paymentForm, flutterwave_secret_key: e.target.value})}
                placeholder="Enter to update"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">PayPal</h3>
            <div>
              <Label htmlFor="paypal_client_id">Client ID</Label>
              <Input
                id="paypal_client_id"
                value={paymentForm.paypal_client_id}
                onChange={(e) => setPaymentForm({...paymentForm, paypal_client_id: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="paypal_client_secret">Client Secret</Label>
              <Input
                id="paypal_client_secret"
                type="password"
                value={paymentForm.paypal_client_secret}
                onChange={(e) => setPaymentForm({...paymentForm, paypal_client_secret: e.target.value})}
                placeholder="Enter to update"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="paypal_sandbox"
                checked={paymentForm.paypal_sandbox}
                onCheckedChange={(checked) => setPaymentForm({...paymentForm, paypal_sandbox: checked})}
              />
              <Label htmlFor="paypal_sandbox">Sandbox Mode</Label>
            </div>
          </div>

          <Button onClick={savePaymentSettings} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Payment Settings'}
          </Button>
        </div>
      </CardContent>
        </Card>
      </div>
    </div>
  );
};