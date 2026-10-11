
import requests


# 1. Calculator function
def calculator(operation: str, a: float, b: float) -> str:
    """Perform addition, subtraction, multiplication, or division."""

    print(f"\n[Calculator called: {operation}, {a}, {b}]")

    if operation == "add":
        return str(a + b)

    elif operation == "subtract":
        return str(a - b)

    elif operation == "multiply":
        return str(a * b)

    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero."
        return str(a / b)

    return "Invalid operation. Use add, subtract, multiply, or divide."


# 2. Weather function
def get_weather(city: str) -> str:
    """Get current weather information for a city."""

    print(f"\n[Weather function called for: {city}]")

    try:
        # Find the city's coordinates
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )
        geo_response.raise_for_status()

        places = geo_response.json().get("results", [])

        if not places:
            return f"City not found: {city}"

        place = places[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        # Get current weather
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "wind_speed_10m,"
                    "weather_code"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()

        current = weather_response.json()["current"]

        # Convert weather codes into descriptions
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Rain showers",
            81: "Moderate rain showers",
            82: "Heavy rain showers",
            85: "Snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with heavy hail",
        }

        condition = weather_codes.get(
            current["weather_code"],
            "Unknown condition",
        )

        return (
            f"Weather in {place['name']}, "
            f"{place.get('country', '')}:\n"
            f"Condition: {condition}\n"
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Feels like: {current['apparent_temperature']}°C\n"
            f"Humidity: {current['relative_humidity_2m']}%\n"
            f"Wind speed: {current['wind_speed_10m']} km/h"
        )

    except requests.RequestException as error:
        return f"Weather service error: {error}"

    except (KeyError, ValueError, IndexError):
        return "Could not read the weather data. Please try again."
