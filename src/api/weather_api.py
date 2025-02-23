from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from typing import Dict, List, Optional
import regex as re

from src.api.service import (
    find_the_most_similar_cities,
    process_non_latin_word,
    read_task_data_from_directory,
    save_task_result,
)
from src.database.crud import (
    create_task,
    get_all_cities,
    get_city_by_name,
    get_task_by_id,
    update_task,
)
from src.tasks import celery_app, fetch_weather_data_for_cities
from src.log import get_logger

logger = get_logger(__name__)

weather_router = APIRouter(tags=["weather"])


@weather_router.post("/weather")
async def request_weather(cities: List[str]):
    # Allow only letters (don't allow numbers and special symbols)
    for city in cities:
        if not re.match(r"^[\p{L} ]+$", city):
            raise HTTPException(
                status_code=400,
                detail=f"'{city}' contains invalid characters. Only letters and spaces are allowed.",
            )

    all_cities = [city.to_dict() for city in await get_all_cities()]

    async def fetch_city_data(city_name: str) -> Optional[Dict]:
        if not all(
            "a" <= city_name_letter.lower() <= "z" for city_name_letter in city_name
        ):
            logger.info(f"City: {city_name} has non-latin letters. Converting.")
            city_name = await process_non_latin_word(city_name)
            logger.info(f"Was converted into {city_name}")

        city_db = await get_city_by_name(city_name)
        if city_db:
            logger.info(f"Found city {city_name} in database.")
            return city_db.to_dict()

        city_db = await find_the_most_similar_cities(city_name, all_cities)
        if city_db:
            logger.info(
                f"Found city with similar name to {city_name} - {city_db["city"]}"
            )
            return city_db

    cities_from_db = []
    for city in cities:
        city_db = await fetch_city_data(city)
        if city_db:
            logger.info(f"City {city_db["city"]} was found.")
            cities_from_db.append(city_db)
            continue
        logger.info(f"Could not find {city} in database.")
        continue

    task = fetch_weather_data_for_cities.delay(cities_from_db)  # type: ignore
    await create_task(task.id, {"status": "running", "results": None})

    logger.info(f"TASK ID: {task.id}")

    return task.id


@weather_router.get("/tasks/{task_id}")
async def request_task(task_id: str) -> Optional[Dict]:
    task = AsyncResult(task_id, app=celery_app)
    task_db = await get_task_by_id(task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.ready():
        await update_task(task_id, {"status": "complete", "results": task.result})
        region_path_map = await save_task_result(task_id, task.result)
        return {"status": "complete", **region_path_map}
    elif task.failed():
        await update_task(task_id, {"status": "failed"})


@weather_router.get("/results/{region}")
async def request_region_results(region: str) -> Optional[Dict]:
    region_data = await read_task_data_from_directory(region)
    if region_data is None:
        logger.info(f"{region} does not exist or is empty.")
    return region_data
