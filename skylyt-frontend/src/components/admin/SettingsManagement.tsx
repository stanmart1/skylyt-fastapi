import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, CreditCard, Shield, Globe, Save } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSettings } from '@/contexts/SettingsContext';
import { useToast } from '@/hooks/use-toast';

interface SettingsData {
  id: number;
  site_name: string;
  site_description: string;
  contact_email: string;
  contact_phone: string;
  maintenance_mode: boolean;
  stripe_public_key: string;
  paystack_public_key: string;
  flutterwave_public_key: string;
  paypal_client_id: string;
  paypal_sandbox: boolean;
  password_min_length: string;
  session_timeout: string;
  two_factor_enabled: boolean;
  login_attempts_limit: string;
  bank_name: string;
  account_name: string;
  account_number: string;
  is_primary_account: boolean;
}

export const SettingsManagement = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { updateSettings } = useSettings();
  const { toast } = useToast();

  const [generalForm, setGeneralForm] = useState({
    site_name: '',
    site_description: '',
    contact_email: '',
    contact_phone: '',
    maintenance_mode: false
  });

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

  const [securityForm, setSecurityForm] = useState({
    password_min_length: '8',
    session_timeout: '30',
    two_factor_enabled: false,
    login_attempts_limit: '5'
  });

  const [bankTransferForm, setBankTransferForm] = useState({
    bank_name: '',
    account_name: '',
    account_number: '',
    is_primary_account: true
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      setSettings(data);
      
      // Populate forms
      setGeneralForm({
        site_name: data.site_name || '',
        site_description: data.site_description || '',
        contact_email: data.contact_email || '',
        contact_phone: data.contact_phone || '',
        maintenance_mode: data.maintenance_mode || false
      });

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

      setSecurityForm({
        password_min_length: data.password_min_length || '8',
        session_timeout: data.session_timeout || '30',
        two_factor_enabled: data.two_factor_enabled || false,
        login_attempts_limit: data.login_attempts_limit || '5'
      });

      setBankTransferForm({
        bank_name: data.bank_name || '',
        account_name: data.account_name || '',
        account_number: data.account_number || '',
        is_primary_account: data.is_primary_account || true
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

  const saveGeneralSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      const response = await apiService.request('/settings/general', {
        method: 'PUT',
        body: JSON.stringify(generalForm)
      });
      
      // Fetch updated settings from database to ensure persistence
      const updatedSettings = await apiService.request('/settings/');
      setSettings(updatedSettings);
      
      // Update global settings context with database values
      updateSettings(updatedSettings);
      
      toast({
        title: "Success",
        description: "General settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update general settings",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
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
      
      // Fetch updated settings from database
      const updatedSettings = await apiService.request('/settings/');
      setSettings(updatedSettings);
      
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

  const saveSecuritySettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/security', {
        method: 'PUT',
        body: JSON.stringify(securityForm)
      });
      
      // Fetch updated settings from database
      const updatedSettings = await apiService.request('/settings/');
      setSettings(updatedSettings);
      
      // Update global settings context
      updateSettings(updatedSettings);
      
      toast({
        title: "Success",
        description: "Security settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update security settings",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const saveBankTransferSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/bank-transfer', {
        method: 'PUT',
        body: JSON.stringify(bankTransferForm)
      });
      
      const updatedSettings = await apiService.request('/settings/');
      setSettings(updatedSettings);
      
      toast({
        title: "Success",
        description: "Bank transfer settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update bank transfer settings",
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
            <Settings className="h-5 w-5" />
            Settings Management
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Settings Management
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="general" className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              General
            </TabsTrigger>
            <TabsTrigger value="payment" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Payment Gateway
            </TabsTrigger>
            <TabsTrigger value="bank-transfer" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Bank Transfer
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security
            </TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="site_name">Site Name</Label>
                <Input
                  id="site_name"
                  value={generalForm.site_name}
                  onChange={(e) => setGeneralForm({...generalForm, site_name: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="site_description">Site Description</Label>
                <Textarea
                  id="site_description"
                  value={generalForm.site_description}
                  onChange={(e) => setGeneralForm({...generalForm, site_description: e.target.value})}
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="contact_email">Contact Email</Label>
                <Input
                  id="contact_email"
                  type="email"
                  value={generalForm.contact_email}
                  onChange={(e) => setGeneralForm({...generalForm, contact_email: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="contact_phone">Contact Phone</Label>
                <Input
                  id="contact_phone"
                  value={generalForm.contact_phone}
                  onChange={(e) => setGeneralForm({...generalForm, contact_phone: e.target.value})}
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  id="maintenance_mode"
                  checked={generalForm.maintenance_mode}
                  onCheckedChange={(checked) => setGeneralForm({...generalForm, maintenance_mode: checked})}
                />
                <Label htmlFor="maintenance_mode">Maintenance Mode</Label>
              </div>
              
              <Button onClick={saveGeneralSettings} disabled={saving}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save General Settings'}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="payment" className="space-y-6">
            {hasPermission('system.manage_settings') ? (
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
            ) : (
              <div className="text-center py-8">
                <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Superadmin access required for payment gateway settings</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="bank-transfer" className="space-y-6">
            {hasPermission('dashboard.view_settings') ? (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="bank_name">Bank Name</Label>
                  <Input
                    id="bank_name"
                    value={bankTransferForm.bank_name}
                    onChange={(e) => setBankTransferForm({...bankTransferForm, bank_name: e.target.value})}
                    placeholder="Enter bank name"
                  />
                </div>
                
                <div>
                  <Label htmlFor="account_name">Account Name</Label>
                  <Input
                    id="account_name"
                    value={bankTransferForm.account_name}
                    onChange={(e) => setBankTransferForm({...bankTransferForm, account_name: e.target.value})}
                    placeholder="Enter account holder name"
                  />
                </div>
                
                <div>
                  <Label htmlFor="account_number">Account Number</Label>
                  <Input
                    id="account_number"
                    value={bankTransferForm.account_number}
                    onChange={(e) => setBankTransferForm({...bankTransferForm, account_number: e.target.value})}
                    placeholder="Enter account number"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_primary_account"
                    checked={bankTransferForm.is_primary_account}
                    onCheckedChange={(checked) => setBankTransferForm({...bankTransferForm, is_primary_account: checked})}
                  />
                  <Label htmlFor="is_primary_account">Primary Account</Label>
                </div>
                
                <Button onClick={saveBankTransferSettings} disabled={saving}>
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Bank Transfer Settings'}
                </Button>
              </div>
            ) : (
              <div className="text-center py-8">
                <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Admin access required for settings management</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="password_min_length">Minimum Password Length</Label>
                <Input
                  id="password_min_length"
                  type="number"
                  value={securityForm.password_min_length}
                  onChange={(e) => setSecurityForm({...securityForm, password_min_length: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="session_timeout">Session Timeout (minutes)</Label>
                <Input
                  id="session_timeout"
                  type="number"
                  value={securityForm.session_timeout}
                  onChange={(e) => setSecurityForm({...securityForm, session_timeout: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="login_attempts_limit">Login Attempts Limit</Label>
                <Input
                  id="login_attempts_limit"
                  type="number"
                  value={securityForm.login_attempts_limit}
                  onChange={(e) => setSecurityForm({...securityForm, login_attempts_limit: e.target.value})}
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  id="two_factor_enabled"
                  checked={securityForm.two_factor_enabled}
                  onCheckedChange={(checked) => setSecurityForm({...securityForm, two_factor_enabled: checked})}
                />
                <Label htmlFor="two_factor_enabled">Enable Two-Factor Authentication</Label>
              </div>
              
              <Button onClick={saveSecuritySettings} disabled={saving}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Security Settings'}
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};