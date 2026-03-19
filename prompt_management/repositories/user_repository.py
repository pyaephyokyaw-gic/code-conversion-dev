"""
User Repository
Handles database operations for user lookups
"""
from repositories.base import get_connection, get_dict_cursor


def get_user_by_cognito_id(cognito_id):
    """Get user info by Cognito sub ID."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT id, organization_id, company_id, name, email, role
                FROM users
                WHERE cognito_id = %s
                """,
                (cognito_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()
