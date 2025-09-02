import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Car, Hotel, Users, Award, Shield, Clock } from 'lucide-react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { apiService } from '@/services/api';

interface AboutSettings {
  page_title: string;
  page_description: string;
  company_story: string;
  mission_statement: string;
  vision_statement: string;
  core_values: string[];
  team_description: string;
  achievements: Array<{
    title: string;
    description: string;
    icon: string;
  }>;
}

const About = () => {
  const [settings, setSettings] = useState<AboutSettings>({
    page_title: 'About Skylyt Luxury',
    page_description: 'Your trusted partner in luxury travel experiences.',
    company_story: 'Founded with a passion for exceptional travel experiences, Skylyt Luxury has been connecting travelers with premium accommodations and luxury vehicles since our inception. We believe that every journey should be memorable, comfortable, and tailored to your unique preferences.',
    mission_statement: 'To provide unparalleled luxury travel experiences through premium accommodations and exceptional service, making every journey extraordinary.',
    vision_statement: 'To be the world\'s leading platform for luxury travel, setting new standards in hospitality and customer satisfaction.',
    core_values: ['Excellence', 'Integrity', 'Innovation', 'Customer Focus', 'Sustainability'],
    team_description: 'Our dedicated team of travel experts works around the clock to ensure your experience exceeds expectations. From our customer service representatives to our partner network, everyone is committed to delivering excellence.',
    achievements: [
      {
        title: '10,000+ Happy Customers',
        description: 'Served customers across multiple countries',
        icon: 'users'
      },
      {
        title: '500+ Premium Hotels',
        description: 'Curated selection of luxury accommodations',
        icon: 'hotel'
      },
      {
        title: '200+ Luxury Vehicles',
        description: 'Fleet of premium cars and chauffeur services',
        icon: 'car'
      },
      {
        title: '24/7 Support',
        description: 'Round-the-clock customer assistance',
        icon: 'clock'
      }
    ]
  });

  useEffect(() => {
    fetchAboutSettings();
  }, []);

  const fetchAboutSettings = async () => {
    try {
      const data = await apiService.request('/about-settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch about settings:', error);
    }
  };

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'users': return <Users className="h-8 w-8" />;
      case 'hotel': return <Hotel className="h-8 w-8" />;
      case 'car': return <Car className="h-8 w-8" />;
      case 'clock': return <Clock className="h-8 w-8" />;
      case 'award': return <Award className="h-8 w-8" />;
      case 'shield': return <Shield className="h-8 w-8" />;
      default: return <Award className="h-8 w-8" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">{settings.page_title}</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">{settings.page_description}</p>
          </div>

          {/* Company Story */}
          <Card className="mb-12">
            <CardHeader>
              <CardTitle>Our Story</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 leading-relaxed">{settings.company_story}</p>
            </CardContent>
          </Card>

          {/* Mission & Vision */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-blue-600" />
                  Our Mission
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">{settings.mission_statement}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-green-600" />
                  Our Vision
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">{settings.vision_statement}</p>
              </CardContent>
            </Card>
          </div>

          {/* Core Values */}
          <Card className="mb-12">
            <CardHeader>
              <CardTitle>Core Values</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {settings.core_values.map((value, index) => (
                  <Badge key={index} variant="secondary" className="px-4 py-2 text-sm">
                    {value}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Achievements */}
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-center mb-8">Our Achievements</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {settings.achievements.map((achievement, index) => (
                <Card key={index} className="text-center">
                  <CardContent className="pt-6">
                    <div className="flex justify-center mb-4 text-blue-600">
                      {getIcon(achievement.icon)}
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{achievement.title}</h3>
                    <p className="text-gray-600 text-sm">{achievement.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Team */}
          <Card>
            <CardHeader>
              <CardTitle>Our Team</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 leading-relaxed">{settings.team_description}</p>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default About;