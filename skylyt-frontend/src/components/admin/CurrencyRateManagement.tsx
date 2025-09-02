import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { DollarSign, Edit, Save, X } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
  rate_to_ngn: number;
  is_active: boolean;
}

export const CurrencyRateManagement: React.FC = () => {
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRate, setEditRate] = useState<string>('');
  
  const canManage = hasPermission('settings.manage_currency');

  useEffect(() => {
    fetchRates();
  }, []);

  const fetchRates = async () => {
    try {
      const data = await apiService.request('/admin/currencies');
      setCurrencies(data);
    } catch (error) {
      console.error('Failed to fetch currencies:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch currencies',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (currency: Currency) => {
    setEditingId(currency.id);
    setEditRate(currency.rate_to_ngn.toString());
  };

  const handleSave = async (id: number) => {
    try {
      await apiService.request(`/admin/currencies/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ rate_to_ngn: parseFloat(editRate) })
      });
      
      setCurrencies(currencies.map(currency => 
        currency.id === id ? { ...currency, rate_to_ngn: parseFloat(editRate) } : currency
      ));
      
      setEditingId(null);
      toast({
        title: 'Success',
        description: 'Exchange rate updated successfully'
      });
    } catch (error) {
      console.error('Failed to update rate:', error);
      toast({
        title: 'Error',
        description: 'Failed to update exchange rate',
        variant: 'destructive'
      });
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditRate('');
  };

  const getCurrencyName = (code: string) => {
    const names = {
      'NGN': 'Nigerian Naira',
      'USD': 'US Dollar',
      'GBP': 'British Pound',
      'EUR': 'Euro'
    };
    return names[code as keyof typeof names] || code;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Currency Exchange Rates</h3>
        <p className="text-gray-600 text-sm">
          Manage manual exchange rates. All conversions use Nigerian Naira (NGN) as the base currency.
        </p>
      </div>

      <div className="grid gap-4">
        {currencies.map((currency) => (
          <Card key={currency.id} className="border-l-4 border-blue-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">{currency.symbol}</span>
                  </div>
                  <div>
                    <h4 className="font-medium">
                      1 {currency.name} = {currency.rate_to_ngn} NGN
                    </h4>
                    <p className="text-sm text-gray-600">
                      {currency.code} → NGN
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {editingId === currency.id ? (
                    <>
                      <div className="flex items-center space-x-2">
                        <Label htmlFor={`rate-${currency.id}`} className="text-sm">Rate to NGN:</Label>
                        <Input
                          id={`rate-${currency.id}`}
                          type="number"
                          step="0.01"
                          value={editRate}
                          onChange={(e) => setEditRate(e.target.value)}
                          className="w-32"
                        />
                      </div>
                      <Button size="sm" onClick={() => handleSave(currency.id)} disabled={!canManage}>
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleCancel}>
                        <X className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => handleEdit(currency)}
                      disabled={currency.code === 'NGN' || !canManage}
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-start space-x-3">
            <DollarSign className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">How Currency Conversion Works</h4>
              <p className="text-sm text-blue-700 mt-1">
                All currency conversions use Nigerian Naira (NGN) as the base currency. 
                When converting between non-NGN currencies, the system first converts to NGN, then to the target currency.
              </p>
              <p className="text-sm text-blue-700 mt-2">
                <strong>Example:</strong> USD to EUR conversion: USD → NGN → EUR
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};