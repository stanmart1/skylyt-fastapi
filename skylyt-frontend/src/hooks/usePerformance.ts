import { useEffect, useCallback } from 'react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  apiResponseTime: number;
}

export const usePerformance = () => {
  const measureApiCall = useCallback(async <T>(
    apiCall: () => Promise<T>,
    endpoint: string
  ): Promise<T> => {
    const startTime = performance.now();
    
    try {
      const result = await apiCall();
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Log performance metrics
      console.log(`API Call [${endpoint}]: ${duration.toFixed(2)}ms`);
      
      // Send to analytics if needed
      if (duration > 2000) {
        console.warn(`Slow API call detected: ${endpoint} took ${duration.toFixed(2)}ms`);
      }
      
      return result;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error(`API Call Failed [${endpoint}]: ${duration.toFixed(2)}ms`, error);
      throw error;
    }
  }, []);

  const measureRender = useCallback((componentName: string) => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      if (duration > 16) { // 60fps threshold
        console.warn(`Slow render detected: ${componentName} took ${duration.toFixed(2)}ms`);
      }
    };
  }, []);

  useEffect(() => {
    // Monitor page load performance
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'navigation') {
          const navEntry = entry as PerformanceNavigationTiming;
          console.log('Page Load Metrics:', {
            domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
            loadComplete: navEntry.loadEventEnd - navEntry.loadEventStart,
            totalTime: navEntry.loadEventEnd - navEntry.fetchStart,
          });
        }
      });
    });

    observer.observe({ entryTypes: ['navigation'] });

    return () => observer.disconnect();
  }, []);

  return {
    measureApiCall,
    measureRender,
  };
};