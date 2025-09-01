import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Bell, Mail, MessageSquare, Settings, Send, Plus, Edit, Trash2 } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/useToast';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

interface NotificationTemplate {
  id: number;
  name: string;
  type: 'email' | 'sms' | 'push';
  event: string;
  subject: string;
  content: string;
  is_active: boolean;
  created_at: string;
}

interface NotificationSettings {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  booking_notifications: boolean;
  payment_notifications: boolean;
  system_notifications: boolean;
}

export const NotificationCenter: React.FC = () => {
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [settings, setSettings] = useState<NotificationSettings>({
    email_enabled: true,
    sms_enabled: false,
    push_enabled: true,
    booking_notifications: true,
    payment_notifications: true,
    system_notifications: true
  });
  const [loading, setLoading] = useState(true);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    type: 'email' as 'email' | 'sms' | 'push',
    event: '',
    subject: '',
    content: '',
    is_active: true
  });
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    description: string;
    action: () => void;
  }>({ open: false, title: '', description: '', action: () => {} });

  useEffect(() => {
    fetchTemplates();
    fetchSettings();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const data = await apiService.request('/admin/notification-templates');
      setTemplates(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch notification templates:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch notification templates',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const data = await apiService.request('/admin/notification-settings');
      setSettings(data || settings);
    } catch (error) {
      console.error('Failed to fetch notification settings:', error);
    }
  };

  const handleSaveSettings = async () => {
    try {
      await apiService.request('/admin/notification-settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      
      toast({
        title: 'Success',
        description: 'Notification settings updated successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save notification settings',
        variant: 'error'
      });
    }
  };

  const handleAddTemplate = () => {
    setEditingTemplate(null);
    setTemplateForm({
      name: '',
      type: 'email',
      event: '',
      subject: '',
      content: '',
      is_active: true
    });
    setIsTemplateModalOpen(true);
  };

  const handleEditTemplate = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    setTemplateForm({
      name: template.name,
      type: template.type,
      event: template.event,
      subject: template.subject,
      content: template.content,
      is_active: template.is_active
    });
    setIsTemplateModalOpen(true);
  };

  const handleSaveTemplate = async () => {
    try {
      if (editingTemplate) {
        await apiService.request(`/admin/notification-templates/${editingTemplate.id}`, {
          method: 'PUT',
          body: JSON.stringify(templateForm)
        });
        toast({
          title: 'Success',
          description: 'Template updated successfully',
          variant: 'success'
        });
      } else {
        await apiService.request('/admin/notification-templates', {
          method: 'POST',
          body: JSON.stringify(templateForm)
        });
        toast({
          title: 'Success',
          description: 'Template created successfully',
          variant: 'success'
        });
      }
      
      setIsTemplateModalOpen(false);
      fetchTemplates();
    } catch (error) {
      console.error('Failed to save template:', error);
      toast({
        title: 'Error',
        description: 'Failed to save template',
        variant: 'error'
      });
    }
  };

  const handleDeleteTemplate = (templateId: number, templateName: string) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Template',
      description: `Are you sure you want to delete the template "${templateName}"?`,
      action: () => deleteTemplate(templateId)
    });
  };

  const deleteTemplate = async (templateId: number) => {
    try {
      await apiService.request(`/admin/notification-templates/${templateId}`, {
        method: 'DELETE'
      });
      
      toast({
        title: 'Success',
        description: 'Template deleted successfully',
        variant: 'success'
      });
      
      fetchTemplates();
    } catch (error) {
      console.error('Failed to delete template:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete template',
        variant: 'error'
      });
    }
  };

  const handleToggleTemplate = async (templateId: number, isActive: boolean) => {
    try {
      await apiService.request(`/admin/notification-templates/${templateId}/toggle`, {
        method: 'PUT',
        body: JSON.stringify({ is_active: isActive })
      });
      
      fetchTemplates();
    } catch (error) {
      console.error('Failed to toggle template:', error);
      toast({
        title: 'Error',
        description: 'Failed to update template status',
        variant: 'error'
      });
    }
  };

  const handleTestNotification = async (templateId: number) => {
    try {
      await apiService.request(`/admin/notification-templates/${templateId}/test`, {
        method: 'POST'
      });
      
      toast({
        title: 'Success',
        description: 'Test notification sent successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to send test notification:', error);
      toast({
        title: 'Error',
        description: 'Failed to send test notification',
        variant: 'error'
      });
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="h-4 w-4" />;
      case 'sms': return <MessageSquare className="h-4 w-4" />;
      case 'push': return <Bell className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'email': return 'bg-blue-100 text-blue-800';
      case 'sms': return 'bg-green-100 text-green-800';
      case 'push': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Notification Center</h2>
          <p className="text-gray-600">Manage notification templates and settings</p>
        </div>
        {hasPermission('notifications.create') && (
          <Button onClick={handleAddTemplate}>
            <Plus className="h-4 w-4 mr-2" />
            Add Template
          </Button>
        )}
      </div>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Notification Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-medium">Notification Channels</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label htmlFor="email-enabled">Email Notifications</Label>
                  <Switch
                    id="email-enabled"
                    checked={settings.email_enabled}
                    onCheckedChange={(checked) => setSettings({ ...settings, email_enabled: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="sms-enabled">SMS Notifications</Label>
                  <Switch
                    id="sms-enabled"
                    checked={settings.sms_enabled}
                    onCheckedChange={(checked) => setSettings({ ...settings, sms_enabled: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="push-enabled">Push Notifications</Label>
                  <Switch
                    id="push-enabled"
                    checked={settings.push_enabled}
                    onCheckedChange={(checked) => setSettings({ ...settings, push_enabled: checked })}
                  />
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-medium">Event Types</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label htmlFor="booking-notifications">Booking Events</Label>
                  <Switch
                    id="booking-notifications"
                    checked={settings.booking_notifications}
                    onCheckedChange={(checked) => setSettings({ ...settings, booking_notifications: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="payment-notifications">Payment Events</Label>
                  <Switch
                    id="payment-notifications"
                    checked={settings.payment_notifications}
                    onCheckedChange={(checked) => setSettings({ ...settings, payment_notifications: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="system-notifications">System Events</Label>
                  <Switch
                    id="system-notifications"
                    checked={settings.system_notifications}
                    onCheckedChange={(checked) => setSettings({ ...settings, system_notifications: checked })}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2 pt-4 border-t mt-6">
            <Button onClick={handleSaveSettings}>
              Save Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Templates ({templates?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
              ))}
            </div>
          ) : !templates || templates.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No notification templates found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {(templates || []).map((template) => (
                <div key={template.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getTypeIcon(template.type)}
                        <h3 className="font-semibold">{template.name}</h3>
                        <Badge className={getTypeColor(template.type)}>
                          {template.type}
                        </Badge>
                        <Badge variant={template.is_active ? 'default' : 'secondary'}>
                          {template.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-2">
                        Event: {template.event}
                      </p>
                      
                      <p className="text-sm font-medium mb-1">Subject: {template.subject}</p>
                      <p className="text-sm text-gray-800 line-clamp-2">{template.content}</p>
                      
                      <p className="text-xs text-gray-500 mt-2">
                        Created: {new Date(template.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <Switch
                        checked={template.is_active}
                        onCheckedChange={(checked) => handleToggleTemplate(template.id, checked)}
                      />
                      
                      {hasPermission('notifications.test') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTestNotification(template.id)}
                        >
                          <Send className="h-3 w-3" />
                        </Button>
                      )}
                      
                      {hasPermission('notifications.update') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditTemplate(template)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                      )}
                      
                      {hasPermission('notifications.delete') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteTemplate(template.id, template.name)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Template Modal */}
      <Dialog open={isTemplateModalOpen} onOpenChange={setIsTemplateModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingTemplate ? 'Edit Template' : 'Add New Template'}</DialogTitle>
            <DialogDescription>
              {editingTemplate ? 'Update the notification template details below.' : 'Create a new notification template for automated messages.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Template Name</Label>
                <Input
                  id="name"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                  placeholder="Enter template name"
                />
              </div>
              <div>
                <Label htmlFor="type">Type</Label>
                <Select value={templateForm.type} onValueChange={(value: any) => setTemplateForm({ ...templateForm, type: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="push">Push Notification</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="event">Event</Label>
              <Select value={templateForm.event} onValueChange={(value) => setTemplateForm({ ...templateForm, event: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select event" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="booking_confirmed">Booking Confirmed</SelectItem>
                  <SelectItem value="booking_cancelled">Booking Cancelled</SelectItem>
                  <SelectItem value="payment_received">Payment Received</SelectItem>
                  <SelectItem value="payment_failed">Payment Failed</SelectItem>
                  <SelectItem value="user_registered">User Registered</SelectItem>
                  <SelectItem value="password_reset">Password Reset</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                value={templateForm.subject}
                onChange={(e) => setTemplateForm({ ...templateForm, subject: e.target.value })}
                placeholder="Enter subject line"
              />
            </div>
            
            <div>
              <Label htmlFor="content">Content</Label>
              <Textarea
                id="content"
                value={templateForm.content}
                onChange={(e) => setTemplateForm({ ...templateForm, content: e.target.value })}
                placeholder="Enter notification content..."
                rows={6}
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch
                id="is_active"
                checked={templateForm.is_active}
                onCheckedChange={(checked) => setTemplateForm({ ...templateForm, is_active: checked })}
              />
              <Label htmlFor="is_active">Active</Label>
            </div>
            
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveTemplate}>
                {editingTemplate ? 'Update Template' : 'Create Template'}
              </Button>
              <Button variant="outline" onClick={() => setIsTemplateModalOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Confirm Dialog */}
      <ConfirmDialog
        open={confirmDialog.open}
        onOpenChange={(open) => setConfirmDialog({ ...confirmDialog, open })}
        title={confirmDialog.title}
        description={confirmDialog.description}
        onConfirm={confirmDialog.action}
      />
    </div>
  );
};