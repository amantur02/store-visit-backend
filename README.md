# Store-Visit-backend

## Installation Steps:

```bash
git clone
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Database Migrations
To generate new migrations:
```bash
alembic revision --autogenerate -m '<MIGRATION_MESSAGE>'
```

To apply migrations: 
```bash
alembic upgrade head
```

## Running Server

```bash
uvicorn main:app --host 0.0.0.0 --reload
```