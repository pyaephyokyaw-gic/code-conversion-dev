"""
Prompt Repository
Handles database operations for prompts table
"""
import os
import boto3
from datetime import datetime
from repositories.base import get_connection, get_dict_cursor

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")
s3 = boto3.client("s3", region_name=AWS_REGION)


def create_prompt(org_id, company_id, name, description, input_file_type, output_file_type, file_url):
    """Insert a new prompt into the database."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM prompts")
            next_id = cur.fetchone()["next_id"]
            cur.execute(
                """
                INSERT INTO prompts
                    (id, organization_id, company_id, prompt_name, prompt_description,
                     input_file_type, output_file_type, prompt_file_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (next_id, org_id, company_id, name, description,
                 input_file_type, output_file_type, file_url, datetime.utcnow()),
            )
            prompt = dict(cur.fetchone())
        conn.commit()
        return prompt
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_prompt_by_id(prompt_id):
    """Get a prompt by ID with organization and company details."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT
                    p.id, p.prompt_name, p.prompt_description,
                    p.input_file_type, p.output_file_type,
                    p.prompt_file_url, p.created_at,
                    o.id   AS organization_id,
                    o.name AS organization_name,
                    c.id   AS company_id,
                    c.name AS company_name
                FROM prompts p
                JOIN organizations o ON o.id = p.organization_id
                JOIN company       c ON c.id = p.company_id
                WHERE p.id = %s
                """,
                (prompt_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_basic_prompt_by_id(prompt_id):
    """Get basic prompt info by ID."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def update_prompt(prompt_id, org_id, company_id, name, description, input_file_type, output_file_type, file_url=None):
    """Update all fields of a prompt in the database."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            if file_url:
                cur.execute(
                    """
                    UPDATE prompts
                    SET organization_id    = COALESCE(%s, organization_id),
                        company_id         = COALESCE(%s, company_id),
                        prompt_name        = COALESCE(%s, prompt_name),
                        prompt_description = COALESCE(%s, prompt_description),
                        input_file_type    = COALESCE(%s, input_file_type),
                        output_file_type   = COALESCE(%s, output_file_type),
                        prompt_file_url    = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (org_id, company_id, name, description, input_file_type, output_file_type, file_url, prompt_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE prompts
                    SET organization_id    = COALESCE(%s, organization_id),
                        company_id         = COALESCE(%s, company_id),
                        prompt_name        = COALESCE(%s, prompt_name),
                        prompt_description = COALESCE(%s, prompt_description),
                        input_file_type    = COALESCE(%s, input_file_type),
                        output_file_type   = COALESCE(%s, output_file_type)
                    WHERE id = %s
                    RETURNING *
                    """,
                    (org_id, company_id, name, description, input_file_type, output_file_type, prompt_id),
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


def delete_prompt(prompt_id):
    """Delete a prompt from the database."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_file_url(prompt_id, file_url):
    """Update only the file URL of a prompt."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                "UPDATE prompts SET prompt_file_url = %s WHERE id = %s",
                (file_url, prompt_id),
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def list_prompts_grouped(org_id=None, company_id=None, search=None, page=1, limit=5):
    """List prompts grouped by organization and company with pagination."""
    offset = (page - 1) * limit

    where = "WHERE 1=1"
    params = []
    if org_id:
        where += " AND o.id = %s"
        params.append(int(org_id))
    if company_id:
        where += " AND c.id = %s"
        params.append(int(company_id))
    if search:
        where += " AND p.prompt_name ILIKE %s"
        params.append(f"%{search}%")

    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            # Get total count of all prompts matching filters
            cur.execute(f"""
                SELECT COUNT(*) AS total
                FROM prompts p
                JOIN organizations o ON o.id = p.organization_id
                JOIN company       c ON c.id = p.company_id
                {where}
            """, params)
            total_prompts = cur.fetchone()["total"]

            # Get distinct org/company pairs
            cur.execute(f"""
                SELECT DISTINCT
                    o.id   AS organization_id,
                    o.name AS organization_name,
                    c.id   AS company_id,
                    c.name AS company_name
                FROM prompts p
                JOIN organizations o ON o.id = p.organization_id
                JOIN company       c ON c.id = p.company_id
                {where}
                ORDER BY o.name, c.name
            """, params)
            companies = [dict(r) for r in cur.fetchall()]

            result = {}
            for comp in companies:
                oid = comp["organization_id"]
                oname = comp["organization_name"]
                cid = comp["company_id"]
                cname = comp["company_name"]

                # Count for this company
                cur.execute(f"""
                    SELECT COUNT(*) AS total
                    FROM prompts p
                    JOIN organizations o ON o.id = p.organization_id
                    JOIN company       c ON c.id = p.company_id
                    {where} AND p.company_id = %s
                """, params + [cid])
                total = cur.fetchone()["total"]

                # Paginated prompts with usage count
                cur.execute(f"""
                    SELECT
                        p.id,
                        p.prompt_name,
                        p.input_file_type,
                        p.output_file_type,
                        p.prompt_description,
                        p.created_at,
                        COUNT(cv.id) AS usage_count
                    FROM prompts p
                    JOIN organizations o ON o.id = p.organization_id
                    JOIN company       c ON c.id = p.company_id
                    LEFT JOIN conversions cv ON cv.prompt_id = p.id
                    {where} AND p.company_id = %s
                    GROUP BY p.id, p.prompt_name, p.input_file_type,
                             p.output_file_type, p.prompt_description, p.created_at
                    ORDER BY p.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [cid, limit, offset])
                prompts = [dict(r) for r in cur.fetchall()]

                result.setdefault(oname, {
                    "organization_id": oid,
                    "companies": []
                })["companies"].append({
                    "company_id": cid,
                    "company_name": cname,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": -(-total // limit),
                    "prompts": prompts,
                })

            grouped_list = [
                {
                    "organization_id": data["organization_id"],
                    "organization_name": oname,
                    "companies": data["companies"],
                }
                for oname, data in result.items()
            ]

        return {"total_prompts": total_prompts, "organizations": grouped_list}
    finally:
        conn.close()


def get_prompt_types_by_company(company_id):
    """Get distinct prompt types (prompt_name with file types) for a company."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT DISTINCT
                    p.id,
                    p.prompt_name,
                    p.prompt_description,
                    p.input_file_type,
                    p.output_file_type
                FROM prompts p
                WHERE p.company_id = %s
                ORDER BY p.prompt_name
                """,
                (company_id,),
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_all_prompt_types():
    """Get all distinct prompt types - for super_admin."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT DISTINCT
                    p.id,
                    p.prompt_name,
                    p.prompt_description,
                    p.input_file_type,
                    p.output_file_type,
                    c.id AS company_id,
                    c.name AS company_name,
                    o.id AS organization_id,
                    o.name AS organization_name
                FROM prompts p
                JOIN company c ON c.id = p.company_id
                JOIN organizations o ON o.id = p.organization_id
                ORDER BY o.name, c.name, p.prompt_name
                """
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_prompt_types_by_organization(organization_id):
    """Get distinct prompt types for an organization."""
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT DISTINCT
                    p.id,
                    p.prompt_name,
                    p.prompt_description,
                    p.input_file_type,
                    p.output_file_type,
                    c.id AS company_id,
                    c.name AS company_name
                FROM prompts p
                JOIN company c ON c.id = p.company_id
                WHERE p.organization_id = %s
                ORDER BY c.name, p.prompt_name
                """,
                (organization_id,),
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def list_prompts_by_company(company_id, search=None, page=1, limit=5):
    """List prompts for a specific company with pagination - for members."""
    offset = (page - 1) * limit
    
    where = "WHERE p.company_id = %s"
    params = [company_id]
    
    if search:
        where += " AND p.prompt_name ILIKE %s"
        params.append(f"%{search}%")
    
    conn = get_connection()
    try:
        with get_dict_cursor(conn) as cur:
            # Get total count
            cur.execute(f"""
                SELECT COUNT(*) AS total
                FROM prompts p
                {where}
            """, params)
            total = cur.fetchone()["total"]
            
            # Get paginated prompts
            cur.execute(f"""
                SELECT
                    p.id,
                    p.prompt_name,
                    p.prompt_description,
                    p.input_file_type,
                    p.output_file_type,
                    p.prompt_file_url,
                    p.created_at,
                    p.organization_id,
                    p.company_id,
                    COUNT(cv.id) AS usage_count
                FROM prompts p
                LEFT JOIN conversions cv ON cv.prompt_id = p.id
                {where}
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            prompts = [dict(r) for r in cur.fetchall()]
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": -(-total // limit) if total > 0 else 0,
                "prompts": prompts
            }
    finally:
        conn.close()
