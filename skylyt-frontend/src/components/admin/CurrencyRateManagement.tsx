import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { DollarSign, Edit, Save, X } from 'lucide-react';

interface CurrencyRate {
  id: number;
  from_currency: string;
  to_currency: string;
  rate: number;
}

export const CurrencyRateManagement: React.FC = () => {
  const { toast } = useToast();
  const [rates, setRates] = useState<CurrencyRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRate, setEditRate] = useState<string>('');

  useEffect(() => {
    fetchRates();
  }, []);

  const fetchRates = async () => {
    try {
      const data = await apiService.request('/admin/currency-rates');
      setRates(data);
    } catch (error) {
      console.error('Failed to fetch currency rates:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch currency rates',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (rate: CurrencyRate) => {
    setEditingId(rate.id);
    setEditRate(rate.rate.toString());
  };

  const handleSave = async (id: number) => {
    try {
      await apiService.request(`/admin/currency-rates/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ rate: parseFloat(editRate) })
      });
      
      setRates(rates.map(rate => 
        rate.id === id ? { ...rate, rate: parseFloat(editRate) } : rate
      ));
      
      setEditingId(null);
      toast({
        title: 'Success',
        description: 'Currency rate updated successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to update rate:', error);
      toast({
        title: 'Error',
        description: 'Failed to update currency rate',
        variant: 'error'
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
        {rates.map((rate) => (
          <Card key={rate.id} className="border-l-4 border-blue-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <DollarSign className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium">
                      1 {getCurrencyName(rate.from_currency)} = {rate.rate} {getCurrencyName(rate.to_currency)}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {rate.from_currency} → {rate.to_currency}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {editingId === rate.id ? (
                    <>
                      <div className="flex items-center space-x-2">
                        <Label htmlFor={`rate-${rate.id}`} className="text-sm">Rate:</Label>
                        <Input
                          id={`rate-${rate.id}`}
                          type="number"
                          step="0.000001"
                          value={editRate}
                          onChange={(e) => setEditRate(e.target.value)}
                          className="w-32"
                        />
                      </div>
                      <Button size="sm" onClick={() => handleSave(rate.id)}>
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleCancel}>
                        <X className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <Button size="sm" variant="outline" onClick={() => handleEdit(rate)}>
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