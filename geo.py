import requests
import functools

@functools.lru_cache(maxsize=1024)
def get_geo(ip: str):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,countryCode,city,isp,org,as,query"},
            timeout=3
        )
        data = r.json()
        if data.get("status") == "success":
            return {
                "country":      data.get("country"),
                "country_code": data.get("countryCode"),
                "city":         data.get("city"),
                "isp":          data.get("isp"),
                "asn":          data.get("as"),
            }
    except requests.RequestException:
        pass
    return {
        "country": None,
        "country_code": None,
        "city": None,
        "isp": None,
        "asn": None,
    }