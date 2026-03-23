import json
from controllers.company_controller import (
    handle_create, handle_list, handle_get,
    handle_update, handle_delete, handle_search,
    handle_by_organization, handle_create_table
)


# ─────────────────────────────────────────────
# RESPONSE HELPER
# ─────────────────────────────────────────────
def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=str)
    }


# ─────────────────────────────────────────────
# LAMBDA HANDLER
# ─────────────────────────────────────────────
def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    # ── Handle CORS preflight ──
    if method == "OPTIONS":
        return response(200, {"message": "CORS preflight OK"})

    # ── Parse body safely ──
    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return response(400, {"error": "Invalid JSON body"})

    try:
        # ─────────────────────────────
        # CREATE TABLE
        # ─────────────────────────────
        if method == "POST" and path.endswith("/create-company-table"):
            result = handle_create_table()
            return response(200, result)

        # ─────────────────────────────
        # SEARCH
        # ─────────────────────────────
        if method == "GET" and path.endswith("/search"):
            result = handle_search(query_params)
            return response(200, result)

        # ─────────────────────────────
        # BY ORGANIZATION
        # ─────────────────────────────
        if method == "GET" and path.endswith("/by-organization"):
            result = handle_by_organization(query_params)
            return response(200, result)

        # ─────────────────────────────
        # LIST
        # ─────────────────────────────
        if method == "GET" and path.endswith("/companies"):
            result = handle_list(query_params)
            return response(200, result)

        # ─────────────────────────────
        # CREATE
        # ─────────────────────────────
        if method == "POST" and path.endswith("/companies"):
            result = handle_create(body)
            return response(200, result)

        # ─────────────────────────────
        # ID ROUTES (/companies/{id})
        # ─────────────────────────────
        if "id" in path_params:
            company_id = path_params["id"]

            # validate id
            if not str(company_id).isdigit():
                return response(400, {"error": "Invalid company id"})

            company_id = int(company_id)

            if method == "GET":
                result = handle_get(company_id)
                return response(200, result)

            if method == "PUT":
                result = handle_update(company_id, body)
                return response(200, result)

            if method == "DELETE":
                result = handle_delete(company_id)
                return response(200, result)

        return response(404, {"message": "Route not found"})

    except Exception as e:
        return response(500, {"error": str(e)})