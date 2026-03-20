"""
Base Repository
Database connection utilities
"""
import os
import psycopg2
import psycopg2.extras

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT", "5432")


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def get_dict_cursor(conn):
    """Return a cursor that returns rows as dictionaries."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
