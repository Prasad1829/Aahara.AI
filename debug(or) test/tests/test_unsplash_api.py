"""
Debug Unsplash API calls
"""
import os
import requests

UNSPLASH_ACCESS_KEY = os.getenv(
    "UNSPLASH_ACCESS_KEY",
    "KnYLVwyWLdcaiXdwBqQsX1Z4BrjbtT924pf6O5DM6uY",
)
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

print("Debug: Testing Unsplash API")
print("=" * 70)
print()

print(f"API Key: {UNSPLASH_ACCESS_KEY[:20]}...{UNSPLASH_ACCESS_KEY[-10:]}")
print(f"Search URL: {UNSPLASH_SEARCH_URL}")
print()

recipe = "Chicken Masala"
print(f"Testing API call for: {recipe}")
print()

try:
    response = requests.get(
        UNSPLASH_SEARCH_URL,
        params={
            "query": f"{recipe} recipe food indian cuisine",
            "per_page": 15,
            "client_id": UNSPLASH_ACCESS_KEY,
            "order_by": "relevant",
        },
        timeout=8,
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    response.raise_for_status()
    data = response.json()
    
    print(f"Response JSON Keys: {data.keys()}")
    print(f"Results Count: {len(data.get('results', []))}")
    print(f"Total Count: {data.get('total', 0)}")
    print()
    
    if data.get('results'):
        for i, result in enumerate(data['results'][:3]):
            img_url = result.get('urls', {}).get('regular', 'N/A')
            print(f"  Image {i+1}: {img_url[:60]}...")
    else:
        print("No results returned from Unsplash")
        print(f"Full JSON: {data}")
        
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
