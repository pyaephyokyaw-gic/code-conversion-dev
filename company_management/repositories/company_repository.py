from datetime import datetime
from repositories.base import get_connection, get_dict_cursor


# ─────────────────────────────────────────────
# CREATE TABLE
# ─────────────────────────────────────────────
def create_company_table():
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    id SERIAL PRIMARY KEY,
                    organization_id INTEGER NOT NULL REFERENCES organizations(id),
                    name VARCHAR(255) NOT NULL,
                    domain VARCHAR(255),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
        return {"message": "Company table ready"}
    finally:
        conn.close()


# ─────────────────────────────────────────────
# CREATE COMPANY
# ─────────────────────────────────────────────
def create_company(data):
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("""
                INSERT INTO company (
                    organization_id,
                    name,
                    domain,
                    description,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (
                int(data["organization_id"]),
                data["name"],
                data.get("domain"),
                data.get("description"),
                datetime.utcnow()
            ))

            result = cur.fetchone()

        conn.commit()
        return dict(result)

    finally:
        conn.close()


# ─────────────────────────────────────────────
# GET BY ID
# ─────────────────────────────────────────────
def get_company_by_id(company_id):
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM company WHERE id = %s",
                (company_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


# ─────────────────────────────────────────────
# UPDATE COMPANY
# ─────────────────────────────────────────────
def update_company(company_id, data):
    conn = get_connection()
    try:
        fields = []
        values = []

        allowed_fields = ["organization_id", "name", "domain", "description"]

        for key in allowed_fields:
            if key in data and data[key] is not None:
                fields.append(f"{key} = %s")

                if key == "organization_id":
                    values.append(int(data[key]))
                else:
                    values.append(data[key])

        if not fields:
            return None  # nothing to update

        values.append(company_id)

        with get_dict_cursor(conn) as cur:
            query = f"""
                UPDATE company
                SET {", ".join(fields)}
                WHERE id = %s
                RETURNING *
            """

            cur.execute(query, values)
            result = cur.fetchone()

        conn.commit()
        return dict(result) if result else None

    finally:
        conn.close()


# ─────────────────────────────────────────────
# DELETE COMPANY
# ─────────────────────────────────────────────
def delete_company(company_id):
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "DELETE FROM company WHERE id = %s RETURNING id",
                (company_id,)
            )
            row = cur.fetchone()

        conn.commit()
        return row is not None

    finally:
        conn.close()


# ─────────────────────────────────────────────
# LIST COMPANIES (WITH SEARCH + PAGINATION)
# ─────────────────────────────────────────────
def list_companies(search=None, page=1, limit=10):
    offset = (page - 1) * limit

    where = "WHERE 1=1"
    params = []

    if search:
        where += " AND name ILIKE %s"
        params.append(f"%{search}%")

    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:

            # COUNT
            cur.execute(f"""
                SELECT COUNT(*) AS total
                FROM company
                {where}
            """, params)

            total = cur.fetchone()["total"]

            # DATA
            cur.execute(f"""
                SELECT *
                FROM company
                {where}
                ORDER BY id
                LIMIT %s OFFSET %s
            """, params + [limit, offset])

            rows = [dict(r) for r in cur.fetchall()]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total else 0,
            "companies": rows
        }

    finally:
        conn.close()


# ─────────────────────────────────────────────
# SEARCH COMPANIES
# ─────────────────────────────────────────────
def search_companies(name):
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM company WHERE name ILIKE %s",
                (f"%{name}%",)
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


# ─────────────────────────────────────────────
# GET BY ORGANIZATION
# ─────────────────────────────────────────────
def get_companies_by_organization(org_id):
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM company WHERE organization_id = %s",
                (org_id,)
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()