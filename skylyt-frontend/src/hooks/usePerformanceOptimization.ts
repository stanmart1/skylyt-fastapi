import { useEffect, useCallback, useRef } from 'react';
import { debounce } from 'lodash';

/**
 * Performance optimization hook for React components
 */
export const usePerformanceOptimization = () => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());

  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    // Log performance warnings for frequent re-renders
    if (timeSinceLastRender < 16 && renderCount.current > 5) {
      console.warn(`Component re-rendered ${renderCount.current} times in ${timeSinceLastRender}ms`);
    }
    
    lastRenderTime.current = now;
  });

  // Debounced search function
  const createDebouncedSearch = useCallback((searchFn: Function, delay: number = 300) => {
    return debounce(searchFn, delay);
  }, []);

  // Optimized event handler
  const createOptimizedHandler = useCallback((handler: Function) => {
    return useCallback((...args: any[]) => {
      // Use requestAnimationFrame for DOM updates
      requestAnimationFrame(() => {
        handler(...args);
      });
    }, [handler]);
  }, []);

  return {
    createDebouncedSearch,
    createOptimizedHandler,
    renderCount: renderCount.current
  };
};

/**
 * Hook for lazy loading images
 */
export const useLazyLoading = () => {
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            const src = img.dataset.src;
            if (src) {
              img.src = src;
              img.removeAttribute('data-src');
              observerRef.current?.unobserve(img);
            }
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1
      }
    );

    return () => {
      observerRef.current?.disconnect();
    };
  }, []);

  const observeImage = useCallback((img: HTMLImageElement | null) => {
    if (img && observerRef.current) {
      observerRef.current.observe(img);
    }
  }, []);

  return { observeImage };
};

/**
 * Hook for optimizing API calls
 */
export const useApiOptimization = () => {
  const requestCache = useRef(new Map<string, { data: any; timestamp: number }>());
  const pendingRequests = useRef(new Map<string, Promise<any>>());

  const cachedRequest = useCallback(async (
    key: string, 
    requestFn: () => Promise<any>, 
    cacheTime: number = 300000 // 5 minutes
  ) => {
    // Check cache first
    const cached = requestCache.current.get(key);
    if (cached && Date.now() - cached.timestamp < cacheTime) {
      return cached.data;
    }

    // Check if request is already pending
    const pending = pendingRequests.current.get(key);
    if (pending) {
      return pending;
    }

    // Make new request
    const request = requestFn().then((data) => {
      requestCache.current.set(key, { data, timestamp: Date.now() });
      pendingRequests.current.delete(key);
      return data;
    }).catch((error) => {
      pendingRequests.current.delete(key);
      throw error;
    });

    pendingRequests.current.set(key, request);
    return request;
  }, []);

  const clearCache = useCallback((key?: string) => {
    if (key) {
      requestCache.current.delete(key);
    } else {
      requestCache.current.clear();
    }
  }, []);

  return { cachedRequest, clearCache };
};