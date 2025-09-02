import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { Save, Plus, X } from 'lucide-react';

interface Achievement {
  title: string;
  description: string;
  icon: string;
}

interface AboutSettings {
  page_title: string;
  page_description: string;
  company_story: string;
  mission_statement: string;
  vision_statement: string;
  core_values: string[];
  team_description: string;
  achievements: Achievement[];
}

export const AboutManagement = () => {
  const [settings, setSettings] = useState<AboutSettings>({
    page_title: '',
    page_description: '',
    company_story: '',
    mission_statement: '',
    vision_statement: '',
    core_values: [],
    team_description: '',
    achievements: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newValue, setNewValue] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await apiService.request('/admin/about-settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch about settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to load about settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiService.request('/admin/about-settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      
      toast({
        title: 'Success',
        description: 'About settings updated successfully',
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update about settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to update about settings',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof AboutSettings, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const addCoreValue = () => {
    if (newValue.trim()) {
      setSettings(prev => ({
        ...prev,
        core_values: [...prev.core_values, newValue.trim()]
      }));
      setNewValue('');
    }
  };

  const removeCoreValue = (index: number) => {
    setSettings(prev => ({
      ...prev,
      core_values: prev.core_values.filter((_, i) => i !== index)
    }));
  };

  const addAchievement = () => {
    setSettings(prev => ({
      ...prev,
      achievements: [...prev.achievements, { title: '', description: '', icon: 'award' }]
    }));
  };

  const updateAchievement = (index: number, field: keyof Achievement, value: string) => {
    setSettings(prev => ({
      ...prev,
      achievements: prev.achievements.map((achievement, i) => 
        i === index ? { ...achievement, [field]: value } : achievement
      )
    }));
  };

  const removeAchievement = (index: number) => {
    setSettings(prev => ({
      ...prev,
      achievements: prev.achievements.filter((_, i) => i !== index)
    }));
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-gray-200 rounded w-1/4" />
        <div className="h-10 bg-gray-200 rounded" />
        <div className="h-4 bg-gray-200 rounded w-1/4" />
        <div className="h-20 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="page_title">Page Title</Label>
              <Input
                id="page_title"
                value={settings.page_title}
                onChange={(e) => handleInputChange('page_title', e.target.value)}
                placeholder="About Skylyt Luxury"
              />
            </div>
            
            <div>
              <Label htmlFor="page_description">Page Description</Label>
              <Textarea
                id="page_description"
                value={settings.page_description}
                onChange={(e) => handleInputChange('page_description', e.target.value)}
                placeholder="Your trusted partner in luxury travel experiences."
                rows={2}
              />
            </div>

            <div>
              <Label htmlFor="company_story">Company Story</Label>
              <Textarea
                id="company_story"
                value={settings.company_story}
                onChange={(e) => handleInputChange('company_story', e.target.value)}
                placeholder="Founded with a passion for exceptional travel experiences..."
                rows={4}
              />
            </div>
          </CardContent>
        </Card>

        {/* Mission & Vision */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Mission Statement</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={settings.mission_statement}
                onChange={(e) => handleInputChange('mission_statement', e.target.value)}
                placeholder="To provide unparalleled luxury travel experiences..."
                rows={4}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Vision Statement</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={settings.vision_statement}
                onChange={(e) => handleInputChange('vision_statement', e.target.value)}
                placeholder="To be the world's leading platform for luxury travel..."
                rows={4}
              />
            </CardContent>
          </Card>
        </div>

        {/* Core Values */}
        <Card>
          <CardHeader>
            <CardTitle>Core Values</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {settings.core_values.map((value, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {value}
                  <button onClick={() => removeCoreValue(index)}>
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="Add new core value"
                onKeyPress={(e) => e.key === 'Enter' && addCoreValue()}
              />
              <Button onClick={addCoreValue} size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Team Description */}
        <Card>
          <CardHeader>
            <CardTitle>Team Description</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={settings.team_description}
              onChange={(e) => handleInputChange('team_description', e.target.value)}
              placeholder="Our dedicated team of travel experts..."
              rows={3}
            />
          </CardContent>
        </Card>

        {/* Achievements */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Achievements</CardTitle>
              <Button onClick={addAchievement} size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Add Achievement
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {settings.achievements.map((achievement, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Achievement {index + 1}</h4>
                  <Button 
                    onClick={() => removeAchievement(index)} 
                    variant="outline" 
                    size="sm"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <Label>Title</Label>
                    <Input
                      value={achievement.title}
                      onChange={(e) => updateAchievement(index, 'title', e.target.value)}
                      placeholder="Achievement title"
                    />
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Input
                      value={achievement.description}
                      onChange={(e) => updateAchievement(index, 'description', e.target.value)}
                      placeholder="Achievement description"
                    />
                  </div>
                  <div>
                    <Label>Icon</Label>
                    <select
                      value={achievement.icon}
                      onChange={(e) => updateAchievement(index, 'icon', e.target.value)}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="users">Users</option>
                      <option value="hotel">Hotel</option>
                      <option value="car">Car</option>
                      <option value="clock">Clock</option>
                      <option value="award">Award</option>
                      <option value="shield">Shield</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};