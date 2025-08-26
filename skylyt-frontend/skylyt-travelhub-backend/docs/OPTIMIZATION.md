# Skylyt TravelHub Performance Optimization Guide

## Database Optimization

### Indexes
The application includes optimized database indexes for:
- User lookups by email and phone
- Booking queries by user, status, and date
- Payment tracking by booking and transaction ID
- RBAC role and permission lookups

### Connection Pooling
- Pool size: 20 connections
- Max overflow: 30 connections
- Connection recycling: 1 hour
- Pre-ping enabled for connection health

### Query Optimization
```python
# Use the QueryOptimizer for complex queries
from app.utils.query_optimizer import QueryOptimizer

# Optimize user bookings with eager loading
query = QueryOptimizer.optimize_user_bookings_query(query)

# Monitor slow queries
@optimize_query
def get_user_bookings(user_id: int):
    # Your query logic here
    pass
```

### Maintenance Commands
```bash
# Run database optimization
make optimize-db

# Create database migration
make migration MESSAGE="add_new_index"

# Apply migrations
make migrate
```

## Caching Strategy

### Multi-Level Caching
1. **Application Cache**: Redis for API responses
2. **Search Cache**: Cached search results with TTL
3. **Session Cache**: User session data
4. **Smart Cache**: Automatic TTL optimization

### Cache Usage
```python
from app.utils.cache_optimizer import cache_search_results, smart_cache

@cache_search_results(ttl=300)
def search_hotels(params):
    # Search logic here
    pass

# Smart caching with statistics
result = await smart_cache.get_with_stats("key")
await smart_cache.set_with_optimization("key", value)
```

### Cache Invalidation
```python
from app.utils.cache_optimizer import CacheOptimizer

# Invalidate by tag
await CacheOptimizer.invalidate_by_tag("user")
await CacheOptimizer.invalidate_by_tag("booking")
```

## Performance Monitoring

### Real-time Monitoring
```bash
# Run performance monitoring
make monitor

# Check system health
curl http://localhost:8000/api/v1/health/detailed

# Get Prometheus metrics
curl http://localhost:8000/api/v1/metrics/prometheus
```

### Key Metrics
- **Response Time**: < 2 seconds for API endpoints
- **Database Queries**: < 10 queries per request
- **Cache Hit Rate**: > 80% for search results
- **Memory Usage**: < 85% of available RAM
- **CPU Usage**: < 80% average

### Performance Headers
The application adds performance headers to responses:
- `X-Response-Time`: Request processing time
- `X-DB-Query-Count`: Number of database queries
- `X-DB-Query-Time`: Total database query time

## Optimization Strategies

### 1. Database Optimization
- **Indexes**: Proper indexing on frequently queried columns
- **Connection Pooling**: Optimized pool size and recycling
- **Query Optimization**: Eager loading and query analysis
- **Regular Maintenance**: VACUUM and ANALYZE operations

### 2. Caching Optimization
- **Smart TTL**: Automatic TTL adjustment based on usage
- **Tag-based Invalidation**: Efficient cache invalidation
- **Hit Rate Monitoring**: Track and optimize cache performance
- **Multi-level Strategy**: Application, search, and session caching

### 3. Application Optimization
- **Async Processing**: Background tasks with Celery
- **Request Optimization**: Middleware for performance tracking
- **Resource Monitoring**: CPU, memory, and disk usage
- **Load Balancing**: Horizontal scaling support

### 4. Infrastructure Optimization
- **Container Optimization**: Multi-stage Docker builds
- **Reverse Proxy**: Nginx for static files and SSL termination
- **Monitoring Stack**: Prometheus and Grafana integration
- **Auto-scaling**: Docker Compose scaling support

## Performance Benchmarks

### Target Performance Metrics
- **API Response Time**: < 500ms (95th percentile)
- **Database Response Time**: < 100ms average
- **Cache Response Time**: < 10ms average
- **Search Results**: < 2 seconds with caching
- **Booking Creation**: < 3 seconds end-to-end

### Load Testing Results
- **Concurrent Users**: 100+ simultaneous users
- **Requests per Second**: 500+ RPS sustained
- **Database Connections**: Efficient pool utilization
- **Memory Usage**: Stable under load
- **Error Rate**: < 0.1% under normal load

## Troubleshooting Performance Issues

### Slow Database Queries
1. Check query execution plans
2. Verify index usage
3. Optimize JOIN operations
4. Consider query refactoring

### High Memory Usage
1. Monitor connection pool size
2. Check for memory leaks
3. Optimize cache usage
4. Review background task memory

### Poor Cache Performance
1. Analyze hit/miss ratios
2. Optimize cache keys
3. Adjust TTL values
4. Review invalidation strategy

### High CPU Usage
1. Profile application code
2. Check for inefficient algorithms
3. Monitor background tasks
4. Consider horizontal scaling

## Best Practices

### Development
- Use performance middleware in development
- Monitor query counts and execution time
- Profile code regularly
- Test with realistic data volumes

### Production
- Enable performance monitoring
- Set up alerting for key metrics
- Regular database maintenance
- Monitor resource usage trends

### Scaling
- Horizontal scaling with load balancer
- Database read replicas for read-heavy workloads
- CDN for static assets
- Microservices architecture for large scale