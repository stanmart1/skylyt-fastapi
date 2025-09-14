import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RefreshCw, Server, Database, AlertTriangle, CheckCircle, FileText, Activity } from 'lucide-react';
import { apiService } from '@/services/api';

interface HealthStatus {
  status: 'healthy' | 'warning' | 'critical';
  database: {
    status: string;
    responseTime: number;
    connections: number;
  };
  redis: {
    status: string;
    responseTime: number;
  };

  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
  uptime: number;
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
};

export const SystemHealth = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [logsModalOpen, setLogsModalOpen] = useState(false);
  const [healthData, setHealthData] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await apiService.getAdminSystemHealth();
      setHealth(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch system health:', error);
      // Set error state for user feedback
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHealthData = async () => {
    try {
      const [healthCheck, dbHealth, readiness, liveness] = await Promise.all([
        apiService.request('/health/'),
        apiService.request('/health/db'),
        apiService.request('/health/ready'),
        apiService.request('/health/live')
      ]);
      setHealthData({ healthCheck, dbHealth, readiness, liveness });
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    }
  };

  const fetchLogs = async () => {
    setLogsLoading(true);
    try {
      // Mock logs - in real implementation, you'd fetch from a logging endpoint
      const mockLogs = [
        `${new Date().toISOString()} - INFO - Application started successfully`,
        `${new Date().toISOString()} - INFO - Database connection established`,
        `${new Date().toISOString()} - INFO - Redis cache connected`,
        `${new Date().toISOString()} - INFO - Health check endpoint active`,
        `${new Date().toISOString()} - INFO - System monitoring enabled`
      ];
      setLogs(mockLogs);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    } finally {
      setLogsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (logsModalOpen) {
      fetchLogs();
      fetchHealthData();
    }
  }, [logsModalOpen]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'ok':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'critical':
      case 'error':
      case 'disconnected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'ok':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  if (loading && !health) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">System Health</h3>
          <RefreshCw className="h-4 w-4 animate-spin" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">System Health</h3>
          <p className="text-sm text-gray-600">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {health ? (
            <Badge className={getStatusColor(health.status)}>
              {getStatusIcon(health.status)}
              <span className="ml-1 capitalize">{health.status}</span>
            </Badge>
          ) : (
            <Badge className="bg-gray-100 text-gray-800">
              <AlertTriangle className="h-4 w-4" />
              <span className="ml-1">Unknown</span>
            </Badge>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setLogsModalOpen(true)}
          >
            <FileText className="h-4 w-4 mr-1" />
            View Logs
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchHealth}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {health ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Database Status */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Database</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Status:</span>
                  <Badge className={getStatusColor(health.database.status)}>
                    {health.database.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Response Time:</span>
                  <span className="text-sm font-medium">{health.database.responseTime}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Connections:</span>
                  <span className="text-sm font-medium">{health.database.connections}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Redis Status */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Redis Cache</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Status:</span>
                  <Badge className={getStatusColor(health.redis.status)}>
                    {health.redis.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Response Time:</span>
                  <span className="text-sm font-medium">{health.redis.responseTime}ms</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Resources */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Resources</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-sm">CPU Usage:</span>
                    <span className={`text-sm font-medium ${
                      health.system.cpu_usage > 85 ? 'text-red-600' : 
                      health.system.cpu_usage > 70 ? 'text-yellow-600' : 'text-green-600'
                    }`}>{health.system.cpu_usage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        health.system.cpu_usage > 85 ? 'bg-red-500' : 
                        health.system.cpu_usage > 70 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${health.system.cpu_usage}%` }}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-sm">Memory:</span>
                    <span className={`text-sm font-medium ${
                      health.system.memory_usage > 85 ? 'text-red-600' : 
                      health.system.memory_usage > 70 ? 'text-yellow-600' : 'text-green-600'
                    }`}>{health.system.memory_usage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        health.system.memory_usage > 85 ? 'bg-red-500' : 
                        health.system.memory_usage > 70 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${health.system.memory_usage}%` }}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-sm">Disk:</span>
                    <span className={`text-sm font-medium ${
                      health.system.disk_usage > 85 ? 'text-red-600' : 
                      health.system.disk_usage > 70 ? 'text-yellow-600' : 'text-green-600'
                    }`}>{health.system.disk_usage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        health.system.disk_usage > 85 ? 'bg-red-500' : 
                        health.system.disk_usage > 70 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${health.system.disk_usage}%` }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Uptime */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Database Uptime</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold">
                {formatUptime(health.uptime)}
              </div>
              <p className="text-xs text-muted-foreground">
                Since database start
              </p>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-gray-600">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
              <p>Unable to load system health data</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Logs and Health Modal */}
      <Dialog open={logsModalOpen} onOpenChange={setLogsModalOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle>System Logs & Health</DialogTitle>
          </DialogHeader>
          <Tabs defaultValue="logs" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="logs">Logs & Monitoring</TabsTrigger>
              <TabsTrigger value="health">Application Health</TabsTrigger>
            </TabsList>
            
            <TabsContent value="logs" className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium">System Logs</h4>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchLogs}
                  disabled={logsLoading}
                >
                  <RefreshCw className={`h-4 w-4 ${logsLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
              <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
                {logsLoading ? (
                  <div className="text-center">Loading logs...</div>
                ) : logs.length > 0 ? (
                  logs.map((log, index) => (
                    <div key={index} className="mb-1">{log}</div>
                  ))
                ) : (
                  <div className="text-center text-gray-500">No logs available</div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="health" className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium">Health Check Status</h4>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchHealthData}
                >
                  <Activity className="h-4 w-4 mr-1" />
                  Check Health
                </Button>
              </div>
              
              {healthData ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Basic Health</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Status:</span>
                          <Badge className={getStatusColor(healthData.healthCheck.status)}>
                            {healthData.healthCheck.status}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Timestamp:</span>
                          <span className="text-sm">{new Date(healthData.healthCheck.timestamp * 1000).toLocaleString()}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Database Health</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Status:</span>
                          <Badge className={getStatusColor(healthData.dbHealth.status)}>
                            {healthData.dbHealth.status}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Database:</span>
                          <Badge className={getStatusColor(healthData.dbHealth.database)}>
                            {healthData.dbHealth.database}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Readiness</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge className={getStatusColor(healthData.readiness.status)}>
                        {healthData.readiness.status}
                      </Badge>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Liveness</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge className={getStatusColor(healthData.liveness.status)}>
                        {healthData.liveness.status}
                      </Badge>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-gray-600">Click "Check Health" to load health data</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
};