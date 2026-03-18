"""
Company Repository
Handles database operations for company table
"""
from repositories.base import get_connection, get_dict_cursor


def find_all_companies():
    """Get all companies ordered by name."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT id, name, organization_id FROM company ORDER BY name")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def find_companies_by_organization(org_id):
    """Get companies by organization ID."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name FROM company WHERE organization_id = %s ORDER BY name",
                (org_id,)
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def find_company_by_id(company_id):
    """Get a company by ID."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, organization_id FROM company WHERE id = %s",
                (company_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()
