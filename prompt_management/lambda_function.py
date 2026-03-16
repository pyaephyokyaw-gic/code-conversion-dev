import json
import os
import boto3
import psycopg2
import psycopg2.extras
from datetime import datetime
from botocore.exceptions import ClientError

DB_HOST     = os.environ.get("DB_HOST")
DB_NAME     = os.environ.get("DB_NAME")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT     = os.environ.get("DB_PORT", "5432")

S3_BUCKET   = os.environ.get("S3_BUCKET_NAME")
AWS_REGION  = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")

s3 = boto3.client("s3", region_name=AWS_REGION)


# ── helpers ──────────────────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

def resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=str),
    }

def s3_url(key):
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"

def presigned_put(key, expires=3600):
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )

def make_key(org_id, filename):
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"prompts/{org_id}/{ts}_{filename}"


# ── CRUD handlers ─────────────────────────────────────────────────────────────

def create_prompt(body):
    """POST /prompts"""
    org_id = body.get("organization_id")
    if not org_id:
        return resp(400, {"error": "organization_id is required"})

    name        = body.get("prompt_name")
    description = body.get("prompt_description")
    filename    = body.get("file_name")          # optional, e.g. "system_prompt.txt"

    file_url     = None
    upload_url   = None
    if filename:
        key        = make_key(org_id, filename)
        file_url   = s3_url(key)
        upload_url = presigned_put(key)

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO prompts
                    (organization_id, prompt_name, prompt_description, prompt_file_url, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (org_id, name, description, file_url, datetime.utcnow()),
            )
            prompt = dict(cur.fetchone())
        conn.commit()
    except Exception as e:
        conn.rollback()
        return resp(500, {"error": str(e)})
    finally:
        conn.close()

    result = {"prompt": prompt}
    if upload_url:
        result["upload_url"] = upload_url
        result["message"] = (
            "File record saved. PUT your file binary to upload_url to store it in S3."
        )
    return resp(201, result)


def list_prompts(query_params):
    """GET /prompts  (optional ?organization_id=<n>)"""
    org_id = query_params.get("organization_id") if query_params else None
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if org_id:
                cur.execute(
                    "SELECT * FROM prompts WHERE organization_id = %s ORDER BY created_at DESC",
                    (org_id,),
                )
            else:
                cur.execute("SELECT * FROM prompts ORDER BY created_at DESC")
            rows = [dict(r) for r in cur.fetchall()]
        return resp(200, {"prompts": rows, "count": len(rows)})
    except Exception as e:
        return resp(500, {"error": str(e)})
    finally:
        conn.close()


def get_prompt(prompt_id):
    """GET /prompts/{id}"""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
            row = cur.fetchone()
        if not row:
            return resp(404, {"error": f"Prompt {prompt_id} not found"})
        return resp(200, {"prompt": dict(row)})
    except Exception as e:
        return resp(500, {"error": str(e)})
    finally:
        conn.close()


def update_prompt(prompt_id, body):
    """PUT /prompts/{id}"""
    name        = body.get("prompt_name")
    description = body.get("prompt_description")
    filename    = body.get("file_name")

    file_url   = None
    upload_url = None

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Verify prompt exists and get org_id for S3 key
            cur.execute("SELECT id, organization_id FROM prompts WHERE id = %s", (prompt_id,))
            existing = cur.fetchone()
            if not existing:
                return resp(404, {"error": f"Prompt {prompt_id} not found"})

            if filename:
                key        = make_key(existing["organization_id"], filename)
                file_url   = s3_url(key)
                upload_url = presigned_put(key)

            if file_url:
                cur.execute(
                    """
                    UPDATE prompts
                    SET prompt_name        = COALESCE(%s, prompt_name),
                        prompt_description = COALESCE(%s, prompt_description),
                        prompt_file_url    = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (name, description, file_url, prompt_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE prompts
                    SET prompt_name        = COALESCE(%s, prompt_name),
                        prompt_description = COALESCE(%s, prompt_description)
                    WHERE id = %s
                    RETURNING *
                    """,
                    (name, description, prompt_id),
                )
            updated = dict(cur.fetchone())
        conn.commit()
    except Exception as e:
        conn.rollback()
        return resp(500, {"error": str(e)})
    finally:
        conn.close()

    result = {"prompt": updated}
    if upload_url:
        result["upload_url"] = upload_url
        result["message"] = "PUT your file binary to upload_url to replace the file in S3."
    return resp(200, result)


def delete_prompt(prompt_id):
    """DELETE /prompts/{id}"""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
            row = cur.fetchone()
            if not row:
                return resp(404, {"error": f"Prompt {prompt_id} not found"})

            # Best-effort S3 deletion
            file_url = dict(row).get("prompt_file_url")
            if file_url:
                try:
                    key = file_url.split(
                        f"{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/"
                    )[1]
                    s3.delete_object(Bucket=S3_BUCKET, Key=key)
                except Exception:
                    pass  # Do not fail the delete if S3 removal errors

            cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
        conn.commit()
        return resp(200, {"message": f"Prompt {prompt_id} deleted successfully"})
    except Exception as e:
        conn.rollback()
        return resp(500, {"error": str(e)})
    finally:
        conn.close()


def generate_upload_url(prompt_id, query_params):
    """GET /prompts/{id}/upload-url?file_name=<name>"""
    filename = (query_params or {}).get("file_name", f"prompt_{prompt_id}.txt")
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
            row = cur.fetchone()
            if not row:
                return resp(404, {"error": f"Prompt {prompt_id} not found"})
            prompt = dict(row)

        key        = make_key(prompt["organization_id"], filename)
        upload_url = presigned_put(key)
        new_url    = s3_url(key)

        with conn.cursor() as cur:
            cur.execute(
                "UPDATE prompts SET prompt_file_url = %s WHERE id = %s",
                (new_url, prompt_id),
            )
        conn.commit()

        return resp(200, {
            "upload_url": upload_url,
            "file_url":   new_url,
            "message":    "PUT your file binary to upload_url. The file_url is already saved to the prompt record.",
        })
    except Exception as e:
        return resp(500, {"error": str(e)})
    finally:
        conn.close()


# ── router ────────────────────────────────────────────────────────────────────

def lambda_handler(event, context):
    method       = event.get("httpMethod", "")
    path         = event.get("path", "")
    path_params  = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return resp(400, {"error": "Invalid JSON body"})

    prompt_id = path_params.get("id")

    # GET /prompts/{id}/upload-url
    if method == "GET" and prompt_id and path.endswith("/upload-url"):
        return generate_upload_url(int(prompt_id), query_params)

    # GET /prompts
    if method == "GET" and not prompt_id:
        return list_prompts(query_params)

    # POST /prompts
    if method == "POST":
        return create_prompt(body)

    # GET /prompts/{id}
    if method == "GET" and prompt_id:
        return get_prompt(int(prompt_id))

    # PUT /prompts/{id}
    if method == "PUT" and prompt_id:
        return update_prompt(int(prompt_id), body)

    # DELETE /prompts/{id}
    if method == "DELETE" and prompt_id:
        return delete_prompt(int(prompt_id))

    return resp(404, {"error": "Route not found"})
