import requests

def get_place_image(place_name):
    """
    Tries Wikimedia first (real landmark images).
    Falls back to Unsplash if not found.
    """

    try:
        # Wikimedia search
        wiki_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": place_name,
            "format": "json"
        }

        r = requests.get(wiki_url, params=params, timeout=5).json()
        results = r.get("query", {}).get("search", [])

        if results:
            title = results[0]["title"]
            return f"https://commons.wikimedia.org/wiki/Special:FilePath/{title.replace(' ', '_')}"
    except:
        pass

    # Fallback → Unsplash smart search
    safe_query = place_name.replace(" ", ",")
    return f"https://source.unsplash.com/1000x500/?{safe_query},landmark,travel"
