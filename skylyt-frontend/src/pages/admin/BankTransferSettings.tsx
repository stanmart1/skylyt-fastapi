import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { CreditCard, Save, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export const BankTransferSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { toast } = useToast();

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

  const saveBankTransferSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/bank-transfer', {
        method: 'PUT',
        body: JSON.stringify(bankTransferForm)
      });
      
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
            <CreditCard className="h-5 w-5" />
            Bank Transfer Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!hasPermission('dashboard.view_settings')) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Bank Transfer Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Admin access required for settings management</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Bank Transfer Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
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
      </CardContent>
    </Card>
  );
};