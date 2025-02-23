from celery import Celery
import requests

from typing import List, Dict, Any

from src.config import get_settings
from src.log import get_logger
from src.api.service import process_open_weather_data

settings = get_settings()
logger = get_logger(__name__)

celery_app = Celery(
    "weather_tasks", broker=settings.REDIS_BROKER, backend=settings.REDIS_BACKEND
)
celery_app.conf.update(
    task_serializer="json",
    result_expires=3600,
)
celery_app.autodiscover_tasks(["src"])


@celery_app.task
def fetch_weather_data_for_cities(cities: List[Dict]) -> Dict[str, Any]:
    request_url = f"https://api.openweathermap.org/data/3.0/onecall?"
    params = {
        "appid": settings.OPEN_WEATHER_API_KEY,
        "units": "metric",
        "exclude": "minutely,hourly,daily",
    }

    region_city_temp_map = {}

    for city in cities:
        logger.info(f"Requesting weather for {city['city']}...")
        params["lon"] = city["lng"]
        params["lat"] = city["lat"]

        try:
            response = requests.get(request_url, params=params)
            logger.info(f"Received response for {city['city']}: {response.status_code}")
            if response.status_code != 200:
                logger.warning(f"Error while getting data for {city['city']}.")
                continue

            city_temperature_data = process_open_weather_data(response.json())
            if "code" in city_temperature_data and "message" in city_temperature_data:
                logger.warning(
                    f"Error while processing data for {city['city']}: {city_temperature_data['code']} - {city_temperature_data['message']}"
                )

            city_temperature_data["city"] = city["city_ascii"]

            if city["region"] not in region_city_temp_map:
                region_city_temp_map[city["region"]] = []
            region_city_temp_map[city["region"]].append(city_temperature_data)

        except Exception as e:
            logger.error(f"Error while fetching data for {city['city']}: {str(e)}")

    return region_city_temp_map
