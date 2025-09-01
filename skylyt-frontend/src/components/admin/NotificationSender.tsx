import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const NotificationSender = () => {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const sendNotification = async () => {
    if (!title || !message) {
      toast({
        title: 'Error',
        description: 'Title and message are required',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      await apiService.sendPushNotification({
        title,
        message,
        segments: ['All'],
        url: url || undefined,
      });

      toast({
        title: 'Success',
        description: 'Push notification sent successfully',
      });

      setTitle('');
      setMessage('');
      setUrl('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to send notification',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Send Push Notification</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          placeholder="Notification title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Textarea
          placeholder="Notification message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Input
          placeholder="URL (optional)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button onClick={sendNotification} disabled={loading}>
          {loading ? 'Sending...' : 'Send Notification'}
        </Button>
      </CardContent>
    </Card>
  );
};