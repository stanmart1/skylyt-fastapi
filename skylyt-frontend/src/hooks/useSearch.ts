import { useState, useCallback } from 'react';
import { SearchParams, Hotel, Car } from '@/types/api';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const useSearch = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [cars, setCars] = useState<Car[]>([]);
  const [totalHotels, setTotalHotels] = useState(0);
  const [totalCars, setTotalCars] = useState(0);
  const { toast } = useToast();

  const searchHotels = useCallback(async (params: SearchParams) => {
    setIsLoading(true);
    try {
      const response = await apiService.searchHotels(params);
      setHotels(response.hotels);
      setTotalHotels(response.total);
    } catch (error) {
      toast({
        title: 'Search failed',
        description: 'Unable to search hotels. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const searchCars = useCallback(async (params: SearchParams) => {
    setIsLoading(true);
    try {
      const response = await apiService.searchCars(params);
      setCars(response.cars);
      setTotalCars(response.total);
    } catch (error) {
      toast({
        title: 'Search failed',
        description: 'Unable to search cars. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    isLoading,
    hotels,
    cars,
    totalHotels,
    totalCars,
    searchHotels,
    searchCars,
  };
};