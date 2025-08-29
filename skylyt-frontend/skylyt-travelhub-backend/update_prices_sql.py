import sqlite3

def update_car_prices():
    # Connect to SQLite database
    conn = sqlite3.connect('skylyt.db')
    cursor = conn.cursor()
    
    # Updated realistic prices in NGN per day
    car_updates = [
        ("BMW X5 2024", 180000),
        ("Tesla Model 3 2024", 150000),
        ("Mercedes-Benz C-Class 2024", 160000),
        ("Porsche 911 2024", 200000),
        ("Audi A4 2024", 140000),
        ("Range Rover Sport 2024", 220000),
        ("Toyota Camry 2024", 80000),
        ("Honda Accord 2024", 75000),
        ("Lexus ES 2024", 120000),
        ("BMW 3 Series 2024", 130000)
    ]
    
    try:
        for car_name, new_price in car_updates:
            cursor.execute(
                "UPDATE cars SET price_per_day = ? WHERE name = ?",
                (new_price, car_name)
            )
            if cursor.rowcount > 0:
                print(f"Updated {car_name}: ₦{new_price}")
        
        conn.commit()
        print(f"\nSuccessfully updated car prices")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_car_prices()