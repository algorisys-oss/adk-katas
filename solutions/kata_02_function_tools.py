from google.adk.agents import Agent

_SAMPLES = {
    "tokyo": "clear, 28 °C",
    "london": "cloudy, 15 °C",
    "new york": "sunny, 25 °C",
}

def get_weather(city: str) -> dict:
    """Returns the weather for a city.

    Args:
        city: The city to look up, e.g. "Tokyo".
    """
    report = _SAMPLES.get(city.lower(), "sunny, 22 °C")
    return {"report": f"The weather in {city} is {report}."}

root_agent = Agent(
    name="weather_bot",
    model="gemini-2.5-flash",
    instruction="Answer weather questions using the get_weather tool.",
    tools=[get_weather],
)
