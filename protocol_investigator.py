import time
from typing import Any

import requests

# --- Configuration (separated from request logic) ---
REQUEST_TIMEOUT = 10

# Open-Meteo: free public weather API (no API key required)..
# Docs: https://open-meteo.com/en/docs
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# GET: current weather via query parameters
CURRENT_WEATHER_PARAMS = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "current_weather": "true",
    "timezone": "America/New_York",
}

# FILTER: request only specific forecast fields and limit days returned
FORECAST_FILTER_PARAMS = {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
    "timezone": "Europe/London",
    "forecast_days": 5,
}

# PAGINATION: slice forecast into separate date windows
FORECAST_PAGE_1_PARAMS = {
    "latitude": 48.8566,
    "longitude": 2.3522,
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "Europe/Paris",
    "start_date": "2026-07-21",
    "end_date": "2026-07-23",
}
FORECAST_PAGE_2_PARAMS = {
    "latitude": 48.8566,
    "longitude": 2.3522,
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "Europe/Paris",
    "start_date": "2026-07-24",
    "end_date": "2026-07-26",
}

# SORT: fetch forecast data, then sort days by max temperature (descending)
FORECAST_SORT_PARAMS = {
    "latitude": 52.52,
    "longitude": 13.41,
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "Europe/Berlin",
    "forecast_days": 7,
}
SORT_ORDER = "desc"

# FILTER: geocoding city search by name
GEOCODING_FILTER_PARAMS = {
    "name": "London",
    "count": 5,
    "language": "en",
    "format": "json",
}

# POST / PUT / PATCH / DELETE (httpbingo test API — weather APIs are GET-only)
POST_URL = "https://httpbingo.org/post"
POST_BODY = {
    "city": "New York",
    "units": "celsius",
    "request_type": "weather_alert",
}

PUT_URL = "https://httpbingo.org/put"
PUT_BODY = {
    "city": "London",
    "units": "celsius",
    "forecast_days": 5,
    "timezone": "Europe/London",
}

PATCH_URL = "https://httpbingo.org/patch"
PATCH_BODY = {
    "forecast_days": 7,
}

DELETE_URL = "https://httpbingo.org/delete"
DELETE_PARAMS = {
    "location_id": "nyc-001",
}


def dispatch_request(
    label: str,
    method: str,
    url: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> requests.Response:
    print(f"\n{'=' * 60}")
    print(f"Initiating payload dispatch... [{label}]")
    print(f"[METHOD]: {method.upper()}")
    if params:
        print(f"[PARAMS]: {params}")
    if json_body:
        print(f"[BODY]: {json_body}")

    start = time.perf_counter()
    response = requests.request(
        method=method,
        url=url,
        params=params,
        json=json_body,
        timeout=REQUEST_TIMEOUT,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    headers = {
        "Server": response.headers.get("Server", ""),
        "Content-Type": response.headers.get("Content-Type", ""),
    }

    print(f"[STATUS]: {response.status_code} {response.reason}")
    print(f"[EXECUTION_TIME]: {elapsed_ms}ms")
    print(f"[HEADERS]: {headers}")

    return response


def print_current_weather_summary(response: requests.Response) -> None:
    data = response.json()
    current = data.get("current_weather", {})
    print(
        f"[RESULT]: {current.get('temperature')}°C, "
        f"wind {current.get('windspeed')} km/h, "
        f"code {current.get('weathercode')}"
    )
    print(f"[TIME]: {current.get('time')} ({data.get('timezone')})")


def print_forecast_summary(response: requests.Response, label: str) -> None:
    daily = response.json().get("daily", {})
    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    print(f"[RESULT]: {label} -> {len(dates)} day(s)")
    for date, high, low in zip(dates, highs, lows):
        print(f"  {date}: high {high}°C, low {low}°C")


def print_sorted_forecast_summary(response: requests.Response) -> None:
    daily = response.json().get("daily", {})
    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    forecast_days = list(zip(dates, highs, lows))
    reverse = SORT_ORDER == "desc"
    sorted_days = sorted(forecast_days, key=lambda day: day[1], reverse=reverse)

    print(f"[SORT]: temperature_2m_max ({SORT_ORDER})")
    print(f"[RESULT]: Berlin forecast -> {len(sorted_days)} day(s)")
    for date, high, low in sorted_days:
        print(f"  {date}: high {high}°C, low {low}°C")


def print_geocoding_summary(response: requests.Response) -> None:
    results = response.json().get("results", [])
    print(f"[FILTER]: name={GEOCODING_FILTER_PARAMS['name']}")
    print(f"[RESULT]: {len(results)} location(s) matched")
    for place in results:
        print(
            f"  {place['name']}, {place.get('country', '')} "
            f"({place['latitude']}, {place['longitude']})"
        )


def run_current_weather() -> None:
    response = dispatch_request(
        "GET current weather - New York",
        "GET",
        WEATHER_URL,
        params=CURRENT_WEATHER_PARAMS,
    )
    if response.ok:
        print_current_weather_summary(response)


def run_forecast_filtering() -> None:
    response = dispatch_request(
        "GET filtered forecast - London",
        "GET",
        WEATHER_URL,
        params=FORECAST_FILTER_PARAMS,
    )
    if response.ok:
        print_forecast_summary(response, "London forecast")


def run_forecast_pagination() -> None:
    page_1 = dispatch_request(
        "GET forecast page 1 - Paris",
        "GET",
        WEATHER_URL,
        params=FORECAST_PAGE_1_PARAMS,
    )
    if page_1.ok:
        print_forecast_summary(page_1, "Paris days 1-3")

    page_2 = dispatch_request(
        "GET forecast page 2 - Paris",
        "GET",
        WEATHER_URL,
        params=FORECAST_PAGE_2_PARAMS,
    )
    if page_2.ok:
        print_forecast_summary(page_2, "Paris days 4-6")


def run_forecast_sorting() -> None:
    response = dispatch_request(
        "GET forecast for sorting - Berlin",
        "GET",
        WEATHER_URL,
        params=FORECAST_SORT_PARAMS,
    )
    if response.ok:
        print_sorted_forecast_summary(response)


def run_geocoding_filter() -> None:
    response = dispatch_request(
        "GET geocoding city search",
        "GET",
        GEOCODING_URL,
        params=GEOCODING_FILTER_PARAMS,
    )
    if response.ok:
        print_geocoding_summary(response)


def run_http_methods() -> None:
    post_response = dispatch_request(
        "POST weather alert subscription",
        "POST",
        POST_URL,
        json_body=POST_BODY,
    )
    if post_response.ok:
        print(f"[RESULT]: server echoed -> {post_response.json().get('json', {})}")

    put_response = dispatch_request(
        "PUT update weather preferences",
        "PUT",
        PUT_URL,
        json_body=PUT_BODY,
    )
    if put_response.ok:
        print(f"[RESULT]: server echoed -> {put_response.json().get('json', {})}")

    patch_response = dispatch_request(
        "PATCH partial preference update",
        "PATCH",
        PATCH_URL,
        json_body=PATCH_BODY,
    )
    if patch_response.ok:
        print(f"[RESULT]: server echoed -> {patch_response.json().get('json', {})}")

    dispatch_request(
        "DELETE remove saved location",
        "DELETE",
        DELETE_URL,
        params=DELETE_PARAMS,
    )


def main() -> None:
    print("Protocol Investigator - Weather API, HTTP Methods, Filter, Sort & Pagination")
    run_current_weather()
    run_forecast_filtering()
    run_forecast_pagination()
    run_forecast_sorting()
    run_geocoding_filter()
    run_http_methods()


if __name__ == "__main__":
    main()
