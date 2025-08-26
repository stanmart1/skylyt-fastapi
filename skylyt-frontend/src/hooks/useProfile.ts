import { useState } from 'react';
import { User } from '@/types/api';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const useProfile = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const updateProfile = async (profileData: Partial<User>) => {
    setIsLoading(true);
    try {
      const updatedUser = await apiService.updateProfile(profileData);
      toast({
        title: 'Profile Updated',
        description: 'Your profile has been updated successfully.',
      });
      return updatedUser;
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: 'Unable to update profile. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    setIsLoading(true);
    try {
      await apiService.changePassword({ current_password: currentPassword, new_password: newPassword });
      toast({
        title: 'Password Changed',
        description: 'Your password has been changed successfully.',
      });
    } catch (error) {
      toast({
        title: 'Password Change Failed',
        description: 'Unable to change password. Please check your current password.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    updateProfile,
    changePassword,
  };
};