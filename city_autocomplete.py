import json
import logging
import urllib.parse
import urllib.request


def fetch_cities(query):
    if not query or len(query) < 2:
        return []
    try:
        params = urllib.parse.urlencode({
            'resource_id': 'd4901968-dad3-4f15-a5f8-ced45e4e8e5c',
            'q': query, 'limit': 100,
            'fields': 'שם_ישוב'
        })
        url = f'https://data.gov.il/api/3/action/datastore_search?{params}'
        req = urllib.request.Request(url, headers={'User-Agent': 'RestaurantApp/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        records = data.get('result', {}).get('records', [])
        return sorted(set(
            r.get('שם_ישוב', '').strip()
            for r in records
            if r.get('שם_ישוב', '').strip()
        ))
    except Exception as e:
        logging.warning(f"Cities API error for '{query}': {e}")
        return []
