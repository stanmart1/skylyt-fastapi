"""
Query Optimization Service
Provides optimized database queries with proper eager loading and caching
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func, text
from typing import List, Dict, Any, Optional
import logging
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.models.hotel import Hotel
from app.models.car import Car
from app.core.redis import cache_get, cache_set
import json
import hashlib

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Optimized database queries with caching and eager loading"""
    
    @staticmethod
    def get_user_bookings_optimized(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get user bookings with optimized eager loading"""
        try:
            query = db.query(Booking).options(
                joinedload(Booking.payments),
                joinedload(Booking.user)
            ).filter(
                Booking.user_id == user_id
            ).order_by(
                Booking.created_at.desc()
            ).limit(limit).offset(offset)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error fetching user bookings: {e}")
            return []
    
    @staticmethod
    def get_booking_with_relations(db: Session, booking_id: int) -> Optional[Booking]:
        """Get booking with all related data in a single query"""
        try:
            return db.query(Booking).options(
                joinedload(Booking.payments),
                joinedload(Booking.user),
                joinedload(Booking.driver)
            ).filter(Booking.id == booking_id).first()
        except Exception as e:
            logger.error(f"Error fetching booking {booking_id}: {e}")
            return None
    
    @staticmethod
    def search_hotels_optimized(
        db: Session, 
        location: str = None,
        min_price: float = None,
        max_price: float = None,
        star_rating: float = None,
        amenities: List[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Optimized hotel search with caching"""
        
        # Create cache key from parameters
        cache_params = {
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'star_rating': star_rating,
            'amenities': amenities,
            'limit': limit,
            'offset': offset
        }
        cache_key = f"hotel_search:{hashlib.md5(json.dumps(cache_params, sort_keys=True).encode()).hexdigest()}"
        
        # Try cache first
        cached_result = cache_get(cache_key)
        if cached_result:
            try:
                return json.loads(cached_result)
            except:
                pass
        
        try:
            # Build optimized query
            query = db.query(Hotel).filter(Hotel.is_available == True)
            
            # Apply filters efficiently
            if location:
                query = query.filter(
                    or_(
                        Hotel.location.ilike(f"%{location}%"),
                        Hotel.city.has(name=location),
                        Hotel.state.has(name=location)
                    )
                )
            
            if min_price is not None:
                query = query.filter(Hotel.price_per_night >= min_price)
            
            if max_price is not None:
                query = query.filter(Hotel.price_per_night <= max_price)
            
            if star_rating is not None:
                query = query.filter(Hotel.star_rating >= star_rating)
            
            if amenities:
                for amenity in amenities:
                    query = query.filter(Hotel.amenities.contains([amenity]))
            
            # Get total count efficiently
            total_query = query.statement.with_only_columns([func.count()]).order_by(None)
            total = db.execute(total_query).scalar()
            
            # Get results with pagination
            hotels = query.order_by(
                Hotel.is_featured.desc(),
                Hotel.star_rating.desc(),
                Hotel.price_per_night.asc()
            ).limit(limit).offset(offset).all()
            
            result = {
                'hotels': [hotel.to_dict() if hasattr(hotel, 'to_dict') else {
                    'id': hotel.id,
                    'name': hotel.name,
                    'location': hotel.location,
                    'star_rating': hotel.star_rating,
                    'price_per_night': hotel.price_per_night,
                    'amenities': hotel.amenities,
                    'is_featured': hotel.is_featured
                } for hotel in hotels],
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
            # Cache result for 5 minutes
            cache_set(cache_key, json.dumps(result), ex=300)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in hotel search: {e}")
            return {'hotels': [], 'total': 0, 'limit': limit, 'offset': offset}
    
    @staticmethod
    def search_cars_optimized(
        db: Session,
        location: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        transmission: str = None,
        fuel_type: str = None,
        seats: int = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Optimized car search with caching"""
        
        # Create cache key
        cache_params = {
            'location': location,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'transmission': transmission,
            'fuel_type': fuel_type,
            'seats': seats,
            'limit': limit,
            'offset': offset
        }
        cache_key = f"car_search:{hashlib.md5(json.dumps(cache_params, sort_keys=True).encode()).hexdigest()}"
        
        # Try cache first
        cached_result = cache_get(cache_key)
        if cached_result:
            try:
                return json.loads(cached_result)
            except:
                pass
        
        try:
            # Build optimized query
            query = db.query(Car).filter(
                and_(
                    Car.is_available == True,
                    Car.status == 'available'
                )
            )
            
            # Apply filters
            if location:
                query = query.filter(Car.location.ilike(f"%{location}%"))
            
            if category:
                query = query.filter(Car.category.ilike(f"%{category}%"))
            
            if min_price is not None:
                query = query.filter(Car.price_per_day >= min_price)
            
            if max_price is not None:
                query = query.filter(Car.price_per_day <= max_price)
            
            if transmission:
                query = query.filter(Car.transmission.ilike(f"%{transmission}%"))
            
            if fuel_type:
                query = query.filter(Car.fuel_type.ilike(f"%{fuel_type}%"))
            
            if seats is not None:
                query = query.filter(Car.seats >= seats)
            
            # Get total count
            total_query = query.statement.with_only_columns([func.count()]).order_by(None)
            total = db.execute(total_query).scalar()
            
            # Get results
            cars = query.order_by(
                Car.is_featured.desc(),
                Car.price_per_day.asc()
            ).limit(limit).offset(offset).all()
            
            result = {
                'cars': [car.to_dict() if hasattr(car, 'to_dict') else {
                    'id': car.id,
                    'name': car.name,
                    'category': car.category,
                    'location': car.location,
                    'price_per_day': car.price_per_day,
                    'transmission': car.transmission,
                    'fuel_type': car.fuel_type,
                    'seats': car.seats,
                    'is_featured': car.is_featured
                } for car in cars],
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
            # Cache result for 5 minutes
            cache_set(cache_key, json.dumps(result), ex=300)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in car search: {e}")
            return {'cars': [], 'total': 0, 'limit': limit, 'offset': offset}
    
    @staticmethod
    def get_admin_bookings_optimized(
        db: Session,
        status: str = None,
        booking_type: str = None,
        start_date: str = None,
        end_date: str = None,
        search: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Optimized admin bookings query with eager loading"""
        
        try:
            # Base query with eager loading
            query = db.query(Booking).options(
                joinedload(Booking.payments),
                joinedload(Booking.user)
            )
            
            # Apply filters
            if status:
                query = query.filter(Booking.status == status)
            
            if booking_type:
                query = query.filter(Booking.booking_type == booking_type)
            
            if start_date:
                query = query.filter(Booking.start_date >= start_date)
            
            if end_date:
                query = query.filter(Booking.end_date <= end_date)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Booking.booking_reference.ilike(search_term),
                        Booking.customer_name.ilike(search_term),
                        Booking.customer_email.ilike(search_term)
                    )
                )
            
            # Get total count
            total_query = query.statement.with_only_columns([func.count()]).order_by(None)
            total = db.execute(total_query).scalar()
            
            # Get results
            bookings = query.order_by(
                Booking.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            return {
                'bookings': bookings,
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error fetching admin bookings: {e}")
            return {'bookings': [], 'total': 0, 'limit': limit, 'offset': offset}
    
    @staticmethod
    def get_payment_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get payment analytics with optimized queries"""
        
        cache_key = f"payment_analytics:{days}"
        cached_result = cache_get(cache_key)
        if cached_result:
            try:
                return json.loads(cached_result)
            except:
                pass
        
        try:
            # Use raw SQL for better performance on analytics
            from datetime import datetime, timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Total revenue
            revenue_query = text("""
                SELECT 
                    COALESCE(SUM(amount), 0) as total_revenue,
                    COUNT(*) as total_payments,
                    AVG(amount) as avg_payment
                FROM payments 
                WHERE status = 'completed' 
                AND created_at >= :start_date
            """)
            
            revenue_result = db.execute(revenue_query, {"start_date": start_date}).fetchone()
            
            # Payment method breakdown
            method_query = text("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM payments 
                WHERE status = 'completed' 
                AND created_at >= :start_date
                GROUP BY payment_method
            """)
            
            method_results = db.execute(method_query, {"start_date": start_date}).fetchall()
            
            # Daily revenue trend
            daily_query = text("""
                SELECT 
                    DATE(created_at) as date,
                    SUM(amount) as daily_revenue,
                    COUNT(*) as daily_count
                FROM payments 
                WHERE status = 'completed' 
                AND created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            
            daily_results = db.execute(daily_query, {"start_date": start_date}).fetchall()
            
            result = {
                'total_revenue': float(revenue_result[0]) if revenue_result[0] else 0,
                'total_payments': revenue_result[1] if revenue_result[1] else 0,
                'avg_payment': float(revenue_result[2]) if revenue_result[2] else 0,
                'payment_methods': [
                    {
                        'method': row[0],
                        'count': row[1],
                        'total_amount': float(row[2])
                    } for row in method_results
                ],
                'daily_trend': [
                    {
                        'date': row[0].isoformat() if row[0] else None,
                        'revenue': float(row[1]) if row[1] else 0,
                        'count': row[2] if row[2] else 0
                    } for row in daily_results
                ]
            }
            
            # Cache for 10 minutes
            cache_set(cache_key, json.dumps(result, default=str), ex=600)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting payment analytics: {e}")
            return {
                'total_revenue': 0,
                'total_payments': 0,
                'avg_payment': 0,
                'payment_methods': [],
                'daily_trend': []
            }