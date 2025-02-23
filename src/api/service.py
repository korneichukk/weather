import Levenshtein
from typing import List, Dict, Any, Optional

from src.config import get_settings
from src.log import get_logger

settings = get_settings()
logger = get_logger(__name__)


def process_open_weather_data(data: Dict) -> Dict:
    response = {}

    try:
        if "cod" in data and data["cod"] != 200:
            response["code"] = data["cod"]
            response["message"] = data.get("message", "Unknown error.")
            return response

        current_temp = data["current"]["temp"]

        if current_temp <= -50 or current_temp >= 50:
            response["code"] = 400
            response["message"] = f"Temperature out of range: {current_temp}°C"
            return response

        weather_description = ""
        if "weather" in data["current"] and len(data["current"]["weather"]) > 0:
            weather_description = data["current"]["weather"][0].get("description", "")

        response["temp"] = current_temp
        response["description"] = weather_description
        return response
    except KeyError as e:
        response["code"] = 500
        response["message"] = f"Missing expected key: {e}"
        return response
    except Exception as e:
        response["code"] = 500
        response["message"] = str(e)
        return response


async def find_the_most_similar_cities(
    city_name: str, cities: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Finds the most similar city name to the provided city_name from a list of city dictionaries.

    Args:
        city_name (str): The city name to compare against the list.
        city_dicts (List[Dict[str, Any]]): A list of dictionaries, each containing 'city' and 'city_ascii' keys.

    Returns:
        Dict[str, Any]: The city that is most similar to the provided city name based on Levenshtein distance.

    Example:
        city_dicts = [{'city': 'New York', 'city_ascii': 'New York', ...}, {'city': 'Los Angeles', 'city_ascii': 'Los Angeles', ...}]
        similar_city = find_most_similar_city('New York', city_dicts)
        print(similar_city)  # Output: {'city': 'New York', 'city_ascii': 'New York', ...}
    """

    most_similar_city = None
    min_distance = float("inf")

    for city_dict in cities:
        city = city_dict.get("city", "")
        city_ascii = city_dict.get("city_ascii", "")

        if not city or not city_ascii:
            continue

        distance_city = Levenshtein.distance(city, city_name)
        distance_city_ascii = Levenshtein.distance(city_ascii, city_name)

        total_distance = distance_city + distance_city_ascii

        if total_distance < min_distance:
            min_distance = total_distance
            most_similar_city = city_dict

    return most_similar_city
