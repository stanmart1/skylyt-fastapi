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
cur.execute('SELECT id FROM cars WHERE make ILIKE %s AND model ILIKE %s', ('%Tesla%', '%Model 3%'))
car = cur.fetchone()

if car:
    car_id = car[0]
    
    # Final working Tesla Model 3 images
    tesla_images = [
        "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&h=600&fit=crop", 
        "https://images.unsplash.com/photo-1593941707882-a5bac6861d75?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1599912027806-cfab8d3df5b1?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&h=600&fit=crop"
    ]
    
    cur.execute('UPDATE cars SET images = %s WHERE id = %s', (json.dumps(tesla_images), car_id))
    conn.commit()
    print("Tesla Model 3 images fixed with working URLs!")

cur.close()
conn.close()