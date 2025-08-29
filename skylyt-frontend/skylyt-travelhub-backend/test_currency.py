import asyncio
import httpx

async def test_exchange_api():
    api_key = "74288c9c5ac689c0174bad7a"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/NGN"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        print("API Response:", data)
        
        if 'conversion_rates' in data:
            rates = data['conversion_rates']
            print(f"NGN to USD: {rates.get('USD', 'Not found')}")
            print(f"NGN to GBP: {rates.get('GBP', 'Not found')}")
            print(f"NGN to EUR: {rates.get('EUR', 'Not found')}")

if __name__ == "__main__":
    asyncio.run(test_exchange_api())