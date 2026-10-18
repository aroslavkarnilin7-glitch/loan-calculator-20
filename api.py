import json
import urllib.request

API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def fetch_rates() -> dict:
    """Получение курсов валют через API ЦБ РФ."""
    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read().decode("utf-8")

    return json.loads(data)