"""
Organization Repository
Handles database operations for organizations table
"""
from datetime import datetime
from repositories.base import get_connection, get_dict_cursor


def create_organization(name):
    """Insert a new organization into the database."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM organizations")
            next_id = cur.fetchone()["next_id"]
            cur.execute(
                """
                INSERT INTO organizations (id, name, created_at)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (next_id, name, datetime.utcnow()),
            )
            org = dict(cur.fetchone())
        conn.commit()
        return org
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_organization_by_id(org_id):
    """Get an organization by ID with company count."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT 
                    o.id, 
                    o.name, 
                    o.created_at,
                    COUNT(c.id) AS company_count
                FROM organizations o
                LEFT JOIN company c ON c.organization_id = o.id
                WHERE o.id = %s
                GROUP BY o.id, o.name, o.created_at
                """,
                (org_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_organization_by_name(name):
    """Get an organization by name."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM organizations WHERE name = %s",
                (name,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def update_organization(org_id, name):
    """Update an organization's name."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                UPDATE organizations
                SET name = COALESCE(%s, name)
                WHERE id = %s
                RETURNING *
                """,
                (name, org_id),
            )
            updated = cur.fetchone()
            result = dict(updated) if updated else None
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_organization(org_id):
    """Delete an organization from the database."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("DELETE FROM organizations WHERE id = %s", (org_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def list_organizations(search=None, page=1, limit=10):
    """List organizations with search and pagination."""
    offset = (page - 1) * limit
    
    where = "WHERE 1=1"
    params = []
    if search:
        where += " AND o.name ILIKE %s"
        params.append(f"%{search}%")

    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            # Get total count
            cur.execute(f"""
                SELECT COUNT(*) AS total
                FROM organizations o
                {where}
            """, params)
            total = cur.fetchone()["total"]

            # Get paginated results with company count
            cur.execute(f"""
                SELECT 
                    o.id, 
                    o.name, 
                    o.created_at,
                    COUNT(c.id) AS company_count
                FROM organizations o
                LEFT JOIN company c ON c.organization_id = o.id
                {where}
                GROUP BY o.id, o.name, o.created_at
                ORDER BY o.name
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            organizations = [dict(r) for r in cur.fetchall()]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": -(-total // limit) if total > 0 else 0,
            "organizations": organizations
        }
    finally:
        conn.close()


def find_all_organizations():
    """Get all organizations for dropdown (simple list)."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT id, name FROM organizations ORDER BY name")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def has_companies(org_id):
    """Check if organization has any companies."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT COUNT(*) AS count FROM company WHERE organization_id = %s",
                (org_id,),
            )
            return cur.fetchone()["count"] > 0
    finally:
        conn.close()
