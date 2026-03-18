"""
Organization Repository
Handles database operations for organizations table
"""
from repositories.base import get_connection, get_dict_cursor


def find_all_organizations():
    """Get all organizations ordered by name."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT id, name FROM organizations ORDER BY name")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def find_organization_by_id(org_id):
    """Get an organization by ID."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT id, name FROM organizations WHERE id = %s", (org_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()
