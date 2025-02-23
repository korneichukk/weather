## Instructions

- Clone
```
git clone https://github.com/korneichukk/weather.git
cd weather
```

- Install dependencies

```
poetry install
poetry shell
```

or

```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Init the database
```
alembic upgrade head
```

- Populate database with cities
```
PYTHONPATH=$(pwd) python src/database/populate.py
```

- Run celery server
```
PYTHONPATH=$(pwd) celery -A src.tasks:celery_app worker --loglevel=info
```

- Run fastapi dev server
```
fastapi dev src/main.py
```
