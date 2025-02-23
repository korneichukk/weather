from typing import Dict, Union, Any, Optional, Sequence, List

from sqlalchemy import Insert, Result, Select, Update, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import AsyncSessionLocal
from src.database.models import City, Task


async def execute(
    query: Union[Select, Update, Insert],
    session: AsyncSession,
    commit_right_after: bool = True,
) -> Result[Any]:
    result = await session.execute(query)
    if commit_right_after:
        await session.commit()
    return result


async def execute_query(
    query: Union[Select, Update, Insert],
    session: Optional[AsyncSession] = None,
    commit_right_after: bool = True,
) -> Result[Any]:
    """
    Executes the provided query using an existing or new database session.

    Args:
        query (Union[Select, Update, Insert]): A SQLAlchemy query object.
        session (Optional[AsyncSession]): An optional existing database session. If not provided,
                                          a new session will be created and closed automatically.
        commit_right_after (bool): Flag to commit right after query execution.

    Returns:
        Result: The result of the query execution.
    """

    if session:
        result = await execute(query, session, commit_right_after)
    else:
        async with AsyncSessionLocal() as local_session:
            result = await execute(query, local_session, commit_right_after)
    return result


async def fetch_one(
    query: Union[Select, Update, Insert], session: Optional[AsyncSession] = None
) -> Optional[Any]:
    """
    Fetches the first item from the result of the provided query.

    Args:
        query (Union[Select, Update]): A SQLAlchemy query object.
        session (Optional[AsyncSession]): An optional existing database session. If not provided,
                                          a new session will be created and closed automatically.

    Returns:
        Optional[Any]: The first item from the query result, or None if no items are found.
    """
    result = await execute_query(query, session)
    return result.scalar_one_or_none()


async def fetch_all(
    query: Union[Select, Update], session: Optional[AsyncSession] = None
) -> Sequence[Any]:
    """
    Fetches all items from the result of the provided query.

    Args:
        query (Union[Select, Update]): A SQLAlchemy query object.
        session (Optional[AsyncSession]): An optional existing database session. If not provided,
                                          a new session will be created and closed automatically.

    Returns:
        List[Any]: A list of all items from the query result.
    """
    result = await execute_query(query, session)
    return result.scalars().all()


async def get_city_by_name(city_name: str) -> Optional[City]:
    """
    Fetches a city row from the database based on a case-insensitive match of the provided city name.
    The function searches for the city name in both the `city` and `city_ascii` columns,
    returning the first match found.

    Args:
        city_name (str): The name of the city to search for in the database.

    Returns:
        Optional[City]: A City object representing the matched city, or None if no match is found.

    Example:
        city = await get_city_by_name("kyiv")
        if city:
            print(f"Found city: {city}")
        else:
            print("City not found.")
    """
    city_name_lower = city_name.lower()
    query = (
        select(City)
        .filter(
            (City.city.ilike(city_name_lower))
            | (City.city_ascii.ilike(city_name_lower))
        )
        .limit(1)
    )
    city_row = await fetch_one(query)
    return city_row


async def get_all_cities() -> List[City]:
    return list(await fetch_all(select(City)))


async def create_task(task_id: str, task_data: Dict[str, Any]):
    query = insert(Task).values(
        id=task_id, status=task_data["status"], results=task_data["results"]
    )
    await execute_query(query)


async def get_task_by_id(task_id: str) -> Optional[Task]:
    query = select(Task).where(Task.id == task_id)
    result = await fetch_one(query)
    return result


async def update_task(task_id: str, task_data: Dict[str, Any]):
    query = (
        update(Task)
        .where(Task.id == task_id)
        .values(status=task_data["status"], results=task_data["results"])
    )
    await execute_query(query)
