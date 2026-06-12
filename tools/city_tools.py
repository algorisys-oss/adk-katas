"""Shared function tools used by the demo agents.

Each tool is a plain typed function with a docstring — ADK reads the
signature and docstring to expose it to the model.
"""

import datetime
from zoneinfo import ZoneInfo

_CITY_TIMEZONES = {
    "new york": "America/New_York",
    "london": "Europe/London",
    "tokyo": "Asia/Tokyo",
    "bengaluru": "Asia/Kolkata",
    "san francisco": "America/Los_Angeles",
}

_CITY_WEATHER = {
    "new york": "sunny, 25 °C (77 °F)",
    "london": "cloudy with light rain, 15 °C (59 °F)",
    "tokyo": "clear, 28 °C (82 °F)",
    "bengaluru": "partly cloudy, 27 °C (81 °F)",
    "san francisco": "foggy, 18 °C (64 °F)",
}


def get_weather(city: str) -> dict:
    """Returns a mock weather report for a city.

    Args:
        city: The name of the city, e.g. "Tokyo".

    Returns:
        A dict with "status" ("success" or "error"). On success a "report"
        string describes the weather; on error an "error_message" explains why.
    """
    report = _CITY_WEATHER.get(city.lower())
    if report is None:
        return {
            "status": "error",
            "error_message": f"No weather data available for '{city}'.",
        }
    return {"status": "success", "report": f"The weather in {city} is {report}."}


def get_current_time(city: str) -> dict:
    """Returns the current local time for a city.

    Args:
        city: The name of the city, e.g. "London".

    Returns:
        A dict with "status". On success a "report" string gives the current
        local time; on error an "error_message" explains the failure.
    """
    tz_name = _CITY_TIMEZONES.get(city.lower())
    if tz_name is None:
        return {
            "status": "error",
            "error_message": f"No timezone information for '{city}'.",
        }
    now = datetime.datetime.now(ZoneInfo(tz_name))
    return {
        "status": "success",
        "report": f"The current time in {city} is {now:%Y-%m-%d %H:%M:%S %Z}.",
    }


def list_supported_cities() -> dict:
    """Returns the list of cities this assistant has data for.

    Returns:
        A dict with "status" and a "cities" list of supported city names.
    """
    return {"status": "success", "cities": sorted(_CITY_WEATHER.keys())}
