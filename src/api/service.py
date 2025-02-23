from collections import defaultdict
import json
import Levenshtein
from typing import List, Dict, Any, Optional
from datetime import datetime
from unidecode import unidecode

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


async def save_task_result(task_id: str, task_result: Dict) -> Dict[str, str]:
    settings.WEATHER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    region_path_map = {}
    for region, region_data in task_result.items():
        region_path = settings.WEATHER_DATA_DIR / region
        region_path.mkdir(parents=True, exist_ok=True)

        file_path = region_path / f"task_{task_id}.json"

        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        for i in range(len(region_data)):
            region_data[i]["time"] = current_time_str

        with open(file_path, "w") as file:
            json.dump(region_data, file)

        logger.info(
            f"Data of task: {task_id} for region: {region} were saved into: {file_path}."
        )
        region_path_map[region] = str(file_path)

    return region_path_map


async def read_task_data_from_directory(
    region_name: str,
) -> Optional[Dict[str, Any]]:
    data = {}
    files_dir = settings.WEATHER_DATA_DIR / region_name

    if not files_dir.exists() or not files_dir.is_dir():
        return

    for file in files_dir.glob("*.json"):
        with open(file, "r") as json_file:
            file_data = json.load(json_file)

            if isinstance(file_data, list):
                for fd in file_data:
                    if fd["city"] not in data:
                        data[fd["city"]] = []
                    data[fd["city"]].append(
                        {key: value for key, value in fd.items() if key != "city"}
                    )
            else:
                logger.info(f"{file.name} does not contain suitable data.")

    return data


async def process_non_latin_word(city_name: str) -> str:
    city_name_processed = unidecode(city_name)
    return city_name_processed
