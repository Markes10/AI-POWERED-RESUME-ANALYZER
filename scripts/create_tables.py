"""
Create database tables for local development using the app's SQLAlchemy models.
This script reads DATABASE_URL from the environment. For XAMPP MySQL on Windows, set:
    set DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
or in PowerShell:
    $env:DATABASE_URL = "mysql+pymysql://root:password@127.0.0.1:3306/swoosh"

Run:
    python scripts/create_tables.py
"""
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise SystemExit('Please set DATABASE_URL environment variable to your MySQL connection string')

print('Using DATABASE_URL:', DATABASE_URL)
engine = create_engine(DATABASE_URL)

print('Importing models...')
import db.models as models  # noqa: E402
from db.database import Base

print('Creating tables... (this may fail if your MySQL user lacks privileges)')
Base.metadata.create_all(bind=engine)
print('Done.')
