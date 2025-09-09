import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CreditCard, Save, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export const BankTransferSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  
  const canManage = hasPermission('settings.manage_bank_transfer');

  const [bankTransferForm, setBankTransferForm] = useState({
    bank_name: '',
    account_name: '',
    account_number: '',
    is_primary_account: true,
    bank_address: '',
    account_type: 'checking',
    currency: 'USD',
    transfer_fee: '0.00',
    processing_time_hours: '24',
    auto_verification_enabled: false,
    require_reference_number: true,
    bank_transfer_instructions: ''
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.getBankTransferSettings();
      
      setBankTransferForm({
        bank_name: data.bank_name || '',
        account_name: data.account_name || '',
        account_number: data.account_number || '',
        is_primary_account: data.is_primary_account || true,
        bank_address: data.bank_address || '',
        account_type: data.account_type || 'checking',
        currency: data.currency || 'USD',
        transfer_fee: data.transfer_fee || '0.00',
        processing_time_hours: data.processing_time_hours || '24',
        auto_verification_enabled: data.auto_verification_enabled ?? false,
        require_reference_number: data.require_reference_number ?? true,
        bank_transfer_instructions: data.bank_transfer_instructions || ''
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
      await apiService.updateBankTransferSettings(bankTransferForm);
      
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

  if (!hasPermission('settings.view_bank_transfer')) {
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
            <p className="text-gray-600">You don't have permission to view bank transfer settings</p>
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
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Bank Account Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="bank_name">Bank Name</Label>
                <Input
                  id="bank_name"
                  value={bankTransferForm.bank_name}
                  onChange={(e) => setBankTransferForm({...bankTransferForm, bank_name: e.target.value})}
                  placeholder="Enter bank name"
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="account_name">Account Name</Label>
                <Input
                  id="account_name"
                  value={bankTransferForm.account_name}
                  onChange={(e) => setBankTransferForm({...bankTransferForm, account_name: e.target.value})}
                  placeholder="Enter account holder name"
                  disabled={!canManage}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="account_number">Account Number</Label>
                <Input
                  id="account_number"
                  value={bankTransferForm.account_number}
                  onChange={(e) => setBankTransferForm({...bankTransferForm, account_number: e.target.value})}
                  placeholder="Enter account number"
                  disabled={!canManage}
                />
              </div>

            </div>

          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Transfer Settings</h3>
            <div>
              <Label htmlFor="bank_transfer_instructions">Transfer Instructions</Label>
              <Textarea
                id="bank_transfer_instructions"
                value={bankTransferForm.bank_transfer_instructions}
                onChange={(e) => setBankTransferForm({...bankTransferForm, bank_transfer_instructions: e.target.value})}
                placeholder="Instructions for customers making bank transfers"
                rows={4}
                disabled={!canManage}
              />
            </div>
          </div>
          
          {canManage && (
            <Button onClick={saveBankTransferSettings} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Bank Transfer Settings'}
            </Button>
          )}
          
          {!canManage && (
            <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
              You don't have permission to modify bank transfer settings. Contact your administrator for access.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};