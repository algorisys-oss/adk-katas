KNOWN = {"tokyo": "clear, 28 °C", "london": "cloudy, 15 °C"}

def get_weather(city: str) -> dict:
    """Returns the weather for a city as a status dict.

    Args:
        city: The city to look up.
    """
    report = KNOWN.get(city.lower())
    if report is None:
        return {
            "status": "error",
            "error_message": f"No weather data for '{city}'.",
        }
    return {"status": "success", "report": f"The weather in {city} is {report}."}
