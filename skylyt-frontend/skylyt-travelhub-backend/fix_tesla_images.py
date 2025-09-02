import psycopg2
import json

conn = psycopg2.connect(
    host='149.102.159.118',
    database='postgres',
    user='postgres',
    password='gWFokHL61BDxNfY3FjQZ66DSuIq2TMzc6Iv6Ij3BvHPXq4Fo75dWPpaU1wsvTNUB',
    port=5321
)
cur = conn.cursor()

# Get Tesla Model 3
cur.execute('SELECT id, images FROM cars WHERE make ILIKE %s AND model ILIKE %s', ('%Tesla%', '%Model 3%'))
car = cur.fetchone()

if car:
    car_id, current_images = car
    print(f"Fixing Tesla Model 3 images...")
    
    # New Tesla Model 3 images
    new_tesla_images = [
        "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&h=600&fit=crop",  # Keep working
        "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&h=600&fit=crop",  # Keep working
        "https://images.unsplash.com/photo-1617886322168-c2a0da7c2e0b?w=800&h=600&fit=crop",  # Replace broken
        "https://images.unsplash.com/photo-1617886903355-9354bb57751f?w=800&h=600&fit=crop",  # Replace broken
        "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&h=600&fit=crop",  # Keep working
        "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&h=600&fit=crop"   # Keep working
    ]
    
    # Update with new Tesla images
    cur.execute('UPDATE cars SET images = %s WHERE id = %s', (json.dumps(new_tesla_images), car_id))
    conn.commit()
    print("Tesla Model 3 images updated successfully!")
    
    # Verify update
    cur.execute('SELECT images FROM cars WHERE id = %s', (car_id,))
    updated_images = cur.fetchone()[0]
    print(f"Updated images ({len(updated_images)} total):")
    for i, img in enumerate(updated_images, 1):
        print(f"  {i}. {img}")
else:
    print("Tesla Model 3 not found")

cur.close()
conn.close()