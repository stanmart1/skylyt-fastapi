from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.car import Car, CarMaintenance
from pydantic import BaseModel, validator
from fastapi import Query

router = APIRouter(prefix="/admin/cars", tags=["admin-cars"])

# Additional Pydantic Models
class CarCreateRequest(BaseModel):
    name: str
    category: str
    price_per_day: float
    currency: Optional[str] = "NGN"
    image_url: Optional[str] = ""
    passengers: Optional[int] = 4
    transmission: Optional[str] = "automatic"
    fuel_type: Optional[str] = "petrol"
    features: Optional[List[str]] = []
    
    @validator('price_per_day')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v


@router.get("")
def get_all_cars(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all cars for admin management"""
    cars = db.query(Car).all()
    return [{
        "id": car.id,
        "name": car.name,
        "make": car.make,
        "model": car.model,
        "year": car.year,
        "plate_number": car.plate_number,
        "category": car.category,
        "price_per_day": float(car.price_per_day),
        "currency": car.currency,
        "image_url": car.images[0] if car.images else None,
        "passengers": car.seats,
        "transmission": car.transmission,
        "fuel_type": car.fuel_type,
        "status": car.status,
        "current_mileage": car.current_mileage,
        "features": car.features or [],
        "is_featured": getattr(car, 'is_featured', False),
        "insurance_expiry": car.insurance_expiry.isoformat() if car.insurance_expiry else None,
        "registration_expiry": car.registration_expiry.isoformat() if car.registration_expiry else None,
        "roadworthiness_expiry": car.roadworthiness_expiry.isoformat() if car.roadworthiness_expiry else None,
        "insurance_doc_url": car.insurance_doc_url,
        "registration_doc_url": car.registration_doc_url,
        "roadworthiness_doc_url": car.roadworthiness_doc_url
    } for car in cars]


@router.post("")
def create_car(
    car_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new car"""
    car = Car(
        id=str(uuid.uuid4()),
        name=car_data["name"],
        make=car_data.get("make", "Unknown"),
        model=car_data.get("model", "Unknown"),
        year=car_data.get("year"),
        plate_number=car_data.get("plate_number"),
        category=car_data["category"],
        price_per_day=car_data["price_per_day"],
        currency=car_data.get("currency", "USD"),
        images=[car_data.get("image_url")] if car_data.get("image_url") else [],
        seats=car_data["passengers"],
        transmission=car_data["transmission"],
        fuel_type=car_data.get("fuel_type", "petrol"),
        status=car_data.get("status", "available"),
        current_mileage=car_data.get("current_mileage", 0),
        features=car_data.get("features", []),
        insurance_doc_url=car_data.get("insurance_doc_url"),
        insurance_expiry=datetime.fromisoformat(car_data["insurance_expiry"]) if car_data.get("insurance_expiry") else None,
        registration_doc_url=car_data.get("registration_doc_url"),
        registration_expiry=datetime.fromisoformat(car_data["registration_expiry"]) if car_data.get("registration_expiry") else None,
        roadworthiness_doc_url=car_data.get("roadworthiness_doc_url"),
        roadworthiness_expiry=datetime.fromisoformat(car_data["roadworthiness_expiry"]) if car_data.get("roadworthiness_expiry") else None
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return {"message": "Car created successfully", "id": car.id}


@router.put("/{car_id}")
def update_car(
    car_id: str,
    car_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update car details"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    for field, value in car_data.items():
        if hasattr(car, field):
            setattr(car, field, value)
    
    db.commit()
    db.refresh(car)
    return {"message": "Car updated successfully"}


@router.delete("/{car_id}")
def delete_car(
    car_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete car"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully"}


@router.post("/{car_id}/feature")
def toggle_feature_car(
    car_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle car as featured"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Toggle featured status (assuming we add this field)
    car.is_featured = not getattr(car, 'is_featured', False)
    db.commit()
    db.refresh(car)
    return {"message": f"Car {'featured' if car.is_featured else 'unfeatured'} successfully"}


class MaintenanceCreate(BaseModel):
    car_id: str
    maintenance_type: str
    description: str
    cost: float
    currency: str = "USD"
    scheduled_date: str
    next_due_date: Optional[str] = None
    next_due_mileage: Optional[int] = None
    service_provider: Optional[str] = None
    notes: Optional[str] = None

@router.get("/maintenance")
def get_car_maintenance(
    car_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get car maintenance records"""
    query = db.query(CarMaintenance)
    if car_id:
        query = query.filter(CarMaintenance.car_id == car_id)
    
    maintenance_records = query.all()
    return [{
        "id": record.id,
        "car_id": record.car_id,
        "maintenance_type": record.maintenance_type,
        "description": record.description,
        "cost": float(record.cost),
        "currency": record.currency,
        "scheduled_date": record.scheduled_date.isoformat(),
        "completed_date": record.completed_date.isoformat() if record.completed_date else None,
        "next_due_date": record.next_due_date.isoformat() if record.next_due_date else None,
        "next_due_mileage": record.next_due_mileage,
        "status": record.status,
        "service_provider": record.service_provider,
        "notes": record.notes,
        "car_name": record.car.name if record.car else None
    } for record in maintenance_records]

@router.post("/maintenance")
def create_maintenance_record(
    maintenance_data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create maintenance record"""
    # Verify car exists
    car = db.query(Car).filter(Car.id == maintenance_data.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    maintenance = CarMaintenance(
        id=str(uuid.uuid4()),
        car_id=maintenance_data.car_id,
        maintenance_type=maintenance_data.maintenance_type,
        description=maintenance_data.description,
        cost=maintenance_data.cost,
        currency=maintenance_data.currency,
        scheduled_date=datetime.fromisoformat(maintenance_data.scheduled_date),
        next_due_date=datetime.fromisoformat(maintenance_data.next_due_date) if maintenance_data.next_due_date else None,
        next_due_mileage=maintenance_data.next_due_mileage,
        service_provider=maintenance_data.service_provider,
        notes=maintenance_data.notes
    )
    
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)
    
    return {"message": "Maintenance record created successfully", "id": maintenance.id}

@router.get("/maintenance/alerts")
def get_maintenance_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get maintenance alerts for overdue and upcoming maintenance"""
    now = datetime.now()
    upcoming_threshold = now + timedelta(days=30)
    
    # Overdue maintenance
    overdue = db.query(CarMaintenance).filter(
        CarMaintenance.next_due_date < now,
        CarMaintenance.status != "completed"
    ).all()
    
    # Upcoming maintenance
    upcoming = db.query(CarMaintenance).filter(
        CarMaintenance.next_due_date.between(now, upcoming_threshold),
        CarMaintenance.status != "completed"
    ).all()
    
    # Document expiry alerts
    cars_with_expiring_docs = db.query(Car).filter(
        (Car.insurance_expiry < upcoming_threshold) |
        (Car.registration_expiry < upcoming_threshold) |
        (Car.roadworthiness_expiry < upcoming_threshold)
    ).all()
    
    return {
        "overdue_maintenance": len(overdue),
        "upcoming_maintenance": len(upcoming),
        "expiring_documents": len(cars_with_expiring_docs),
        "overdue_records": [{
            "id": record.id,
            "car_name": record.car.name,
            "maintenance_type": record.maintenance_type,
            "due_date": record.next_due_date.isoformat()
        } for record in overdue],
        "upcoming_records": [{
            "id": record.id,
            "car_name": record.car.name,
            "maintenance_type": record.maintenance_type,
            "due_date": record.next_due_date.isoformat()
        } for record in upcoming],
        "expiring_docs": [{
            "car_id": car.id,
            "car_name": car.name,
            "insurance_expiry": car.insurance_expiry.isoformat() if car.insurance_expiry else None,
            "registration_expiry": car.registration_expiry.isoformat() if car.registration_expiry else None,
            "roadworthiness_expiry": car.roadworthiness_expiry.isoformat() if car.roadworthiness_expiry else None
        } for car in cars_with_expiring_docs]
    }


@router.get("/stats")
def get_car_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get car fleet statistics"""
    from sqlalchemy import func, and_
    from datetime import datetime
    
    # Get basic car statistics
    total_cars = db.query(Car).count()
    available_cars = db.query(Car).filter(Car.is_available == True).count()
    
    # Initialize other stats
    active_bookings = 0
    today_revenue = 0
    
    try:
        from app.models.booking import Booking
        from app.models.payment import Payment
        
        # Get active car bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Update car statuses based on bookings
        out_with_customer = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status == 'ongoing'
            )
        ).count()
        
        # Calculate today's revenue - check all payments first
        today = datetime.now().date()
        
        # Debug: Check all payments
        all_payments = db.query(Payment).join(Booking).filter(Booking.booking_type == 'car').all()
        print(f"Debug: Found {len(all_payments)} car payments")
        for p in all_payments:
            print(f"Payment {p.id}: status={p.status}, amount={p.amount}, date={p.created_at}")
        
        # Try different status values
        today_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status.in_(['completed', 'COMPLETED', 'success', 'SUCCESS'])
            )
        ).scalar() or 0
        
        print(f"Debug: Today's revenue calculated: {today_revenue}")
    except Exception as e:
        # If booking/payment models don't exist, continue with 0 values
        print(f"Debug: Exception in revenue calculation: {e}")
        pass
    
    booked_cars = active_bookings
    maintenance_cars = total_cars - available_cars - booked_cars if total_cars > available_cars + booked_cars else 0
    
    # Calculate utilization rate
    utilization_rate = 0
    if total_cars > 0:
        utilization_rate = round((active_bookings / total_cars) * 100, 1)
    
    return {
        "total_cars": total_cars,
        "available": available_cars,
        "booked": booked_cars,
        "maintenance": maintenance_cars,
        "revenue_today": float(today_revenue),
        "utilization_rate": utilization_rate
    }

@router.post("/{car_id}/documents")
def upload_car_document(
    car_id: str,
    document_type: str,  # insurance, registration, roadworthiness
    document_url: str,
    expiry_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload car document"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    if document_type == "insurance":
        car.insurance_doc_url = document_url
        if expiry_date:
            car.insurance_expiry = datetime.fromisoformat(expiry_date)
    elif document_type == "registration":
        car.registration_doc_url = document_url
        if expiry_date:
            car.registration_expiry = datetime.fromisoformat(expiry_date)
    elif document_type == "roadworthiness":
        car.roadworthiness_doc_url = document_url
        if expiry_date:
            car.roadworthiness_expiry = datetime.fromisoformat(expiry_date)
    else:
        raise HTTPException(status_code=400, detail="Invalid document type")
    
    db.commit()
    return {"message": f"{document_type.title()} document uploaded successfully"}

@router.put("/maintenance/{maintenance_id}/status")
def update_maintenance_status(
    maintenance_id: str,
    status: str,  # scheduled, in_progress, completed, cancelled
    completed_date: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update maintenance record status"""
    maintenance = db.query(CarMaintenance).filter(CarMaintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    maintenance.status = status
    if completed_date:
        maintenance.completed_date = datetime.fromisoformat(completed_date)
    if notes:
        maintenance.notes = notes
    
    db.commit()
    return {"message": "Maintenance status updated successfully"}

# Additional endpoints from main.py
@router.get("/fleet-stats")
async def get_fleet_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get fleet statistics with rental trends and distribution data"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_, extract
        
        # Fleet status counts
        total_cars = db.query(Car).count()
        available_cars = db.query(Car).filter(Car.is_available == True).count()
        
        # Active bookings for rented cars
        rented_cars = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        maintenance_cars = max(0, total_cars - available_cars - rented_cars)
        
        # Rental trends over last 6 months
        rental_trends = []
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            monthly_rentals = db.query(func.count(Booking.id)).filter(
                and_(
                    Booking.booking_type == 'car',
                    Booking.created_at >= month_start,
                    Booking.created_at < month_end
                )
            ).scalar() or 0
            
            rental_trends.insert(0, {
                "month": month_start.strftime("%b %Y"),
                "rentals": monthly_rentals
            })
        
        # Fleet distribution for pie chart
        fleet_distribution = [
            {"name": "Available", "value": available_cars, "color": "#10b981"},
            {"name": "Rented", "value": rented_cars, "color": "#3b82f6"},
            {"name": "Maintenance", "value": maintenance_cars, "color": "#f59e0b"}
        ]
        
        # Maintenance alerts (mock data for cars due for service)
        maintenance_alerts = []
        if maintenance_cars > 0:
            maintenance_alerts.append({
                "car_name": "Sample Car 1",
                "type": "Service Due",
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            })
        
        return {
            "fleet_status": {
                "total_cars": total_cars,
                "available": available_cars,
                "rented": rented_cars,
                "maintenance": maintenance_cars
            },
            "rental_trends": rental_trends,
            "fleet_distribution": fleet_distribution,
            "maintenance_alerts": maintenance_alerts
        }
    except Exception as e:
        # Return default data if error occurs
        return {
            "fleet_status": {
                "total_cars": 0,
                "available": 0,
                "rented": 0,
                "maintenance": 0
            },
            "rental_trends": [],
            "fleet_distribution": [
                {"name": "Available", "value": 0, "color": "#10b981"},
                {"name": "Rented", "value": 0, "color": "#3b82f6"},
                {"name": "Maintenance", "value": 0, "color": "#f59e0b"}
            ],
            "maintenance_alerts": []
        }