from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.car import Car

def update_car_prices():
    db = SessionLocal()
    try:
        # Updated realistic prices in NGN per day
        car_prices = {
            "BMW X5 2024": 180000,
            "Tesla Model 3 2024": 150000,
            "Mercedes-Benz C-Class 2024": 160000,
            "Porsche 911 2024": 200000,
            "Audi A4 2024": 140000,
            "Range Rover Sport 2024": 220000,
            "Toyota Camry 2024": 80000,
            "Honda Accord 2024": 75000,
            "Lexus ES 2024": 120000,
            "BMW 3 Series 2024": 130000
        }
        
        cars = db.query(Car).all()
        updated_count = 0
        
        for car in cars:
            if car.name in car_prices:
                old_price = car.price_per_day
                car.price_per_day = car_prices[car.name]
                print(f"Updated {car.name}: ₦{old_price} -> ₦{car.price_per_day}")
                updated_count += 1
        
        db.commit()
        print(f"\nSuccessfully updated {updated_count} car prices")
        
    except Exception as e:
        print(f"Error updating car prices: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_car_prices()