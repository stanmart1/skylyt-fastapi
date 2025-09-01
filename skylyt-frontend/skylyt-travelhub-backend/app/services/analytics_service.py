from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models.user import User
from app.utils.cache_manager import cache_result
try:
    from app.models.booking import Booking
except ImportError:
    Booking = None
try:
    from app.models.payment import Payment
except ImportError:
    Payment = None


class AnalyticsService:
    @staticmethod
    def get_dashboard_analytics(db: Session, time_range: str = "6m") -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        
        # Calculate date range
        end_date = datetime.utcnow()
        if time_range == "1m":
            start_date = end_date - timedelta(days=30)
        elif time_range == "3m":
            start_date = end_date - timedelta(days=90)
        elif time_range == "6m":
            start_date = end_date - timedelta(days=180)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=180)  # Default to 6 months
        
        # Initialize empty data structures
        bookings_data = []
        user_growth_data = []
        payment_methods_data = []
        destinations_data = []
        
        # Get user growth by month (this should always work)
        try:
            users_by_month = db.query(
                extract('year', User.created_at).label('year'),
                extract('month', User.created_at).label('month'),
                func.count(User.id).label('users')
            ).filter(
                User.created_at >= start_date
            ).group_by(
                extract('year', User.created_at),
                extract('month', User.created_at)
            ).order_by(
                extract('year', User.created_at),
                extract('month', User.created_at)
            ).all()
            
            # Convert to month names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for user_data in users_by_month:
                month_name = month_names[int(user_data.month) - 1]
                year = int(user_data.year)
                user_growth_data.append({
                    "month": f"{month_name} {year}",
                    "users": user_data.users
                })
                

        except Exception as e:
            print(f"Error fetching user data: {e}")
        

        
        # Calculate metrics from real user data only
        total_users = db.query(func.count(User.id)).filter(User.created_at >= start_date).scalar() or 0
        total_bookings = 0
        total_revenue = 0
        avg_booking_value = 0
        
        return {
            "bookings": [],
            "userGrowth": user_growth_data,
            "paymentMethods": [],
            "topDestinations": [],
            "metrics": {
                "totalBookings": total_bookings,
                "totalRevenue": float(total_revenue),
                "totalUsers": total_users,
                "avgBookingValue": round(avg_booking_value, 2)
            }
        }
    
    @staticmethod
    @cache_result("admin_stats", ttl=300)
    def get_admin_stats(db: Session) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        
        # Get current month stats
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Real bookings data only
        current_bookings = 0
        last_bookings = 0
        current_revenue = 0
        last_revenue = 0
        
        if Booking:
            current_bookings = db.query(func.count(Booking.id)).filter(
                Booking.created_at >= current_month_start
            ).scalar() or 0
            
            last_bookings = db.query(func.count(Booking.id)).filter(
                Booking.created_at >= last_month_start,
                Booking.created_at < current_month_start
            ).scalar() or 0
            
            current_revenue = db.query(func.sum(Booking.total_amount)).filter(
                Booking.created_at >= current_month_start
            ).scalar() or 0
            
            last_revenue = db.query(func.sum(Booking.total_amount)).filter(
                Booking.created_at >= last_month_start,
                Booking.created_at < current_month_start
            ).scalar() or 0
        
        # Active users (all active users as fallback)
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        
        # Total fleet size (cars + hotels)
        try:
            from app.models.car import Car
            total_cars = db.query(func.count(Car.id)).scalar() or 0
        except ImportError:
            total_cars = 0
        
        try:
            from app.models.hotel import Hotel
            total_hotels = db.query(func.count(Hotel.id)).scalar() or 0
        except ImportError:
            total_hotels = 0
            
        fleet_size = total_cars + total_hotels
        
        # Calculate percentage changes
        booking_change = ((current_bookings - last_bookings) / last_bookings * 100) if last_bookings > 0 else 0
        revenue_change = ((float(current_revenue) - float(last_revenue)) / float(last_revenue) * 100) if last_revenue > 0 else 0
        
        return {
            "totalBookings": current_bookings,
            "bookingChange": round(booking_change, 1),
            "totalRevenue": float(current_revenue),
            "revenueChange": round(revenue_change, 1),
            "activeUsers": active_users,
            "fleetSize": fleet_size,
            "totalCars": total_cars,
            "totalHotels": total_hotels
        }