class OneSignalService {
  private apiKey = import.meta.env.ONE_SIGNAL_API_KEY;
  private appId = import.meta.env.VITE_ONESIGNAL_APP_ID;
  private baseURL = 'https://onesignal.com/api/v1';
  
  private isConfigured(): boolean {
    return !!(this.apiKey && this.appId && 
             this.apiKey !== 'your-onesignal-api-key' && 
             this.appId !== 'your-onesignal-app-id' &&
             this.apiKey !== 'undefined' &&
             this.appId !== 'undefined');
  }

  async sendNotification(data: {
    title: string;
    message: string;
    userIds?: string[];
    segments?: string[];
    url?: string;
  }) {
    if (!this.isConfigured()) {
      throw new Error('OneSignal is not properly configured');
    }
    
    try {
      const response = await fetch(`${this.baseURL}/notifications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${this.apiKey}`,
        },
        body: JSON.stringify({
          app_id: this.appId,
          headings: { en: data.title },
          contents: { en: data.message },
          ...(data.userIds && { include_player_ids: data.userIds }),
          ...(data.segments && { included_segments: data.segments }),
          ...(data.url && { url: data.url }),
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`OneSignal API error: ${response.statusText} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send notification:', error);
      throw error;
    }
  }

  async sendToAllUsers(title: string, message: string, url?: string) {
    if (!this.isConfigured()) {
      throw new Error('OneSignal is not properly configured');
    }
    
    return this.sendNotification({
      title,
      message,
      segments: ['All'],
      url,
    });
  }

  async sendToUser(userId: string, title: string, message: string, url?: string) {
    if (!this.isConfigured()) {
      throw new Error('OneSignal is not properly configured');
    }
    
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    return this.sendNotification({
      title,
      message,
      userIds: [userId],
      url,
    });
  }
}

export const oneSignalService = new OneSignalService();