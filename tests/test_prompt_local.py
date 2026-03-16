"""
Local test runner for PromptFunction — no SAM, no real S3.
Run:  python tests/test_prompt_local.py

Requirements:
  pip install psycopg2-binary python-dotenv
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

# ── Load .env ──────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Add prompt_management to path ─────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prompt_management"))


# ── Helpers ────────────────────────────────────────────────────────────────────

def fake_presigned_url(operation, Params, ExpiresIn):
    bucket = Params["Bucket"]
    key    = Params["Key"]
    return f"https://{bucket}.s3.amazonaws.com/{key}?X-Amz-Signature=FAKE"

def make_event(method, path, path_params=None, body=None, query=None):
    return {
        "httpMethod":            method,
        "path":                  path,
        "pathParameters":        path_params or {},
        "queryStringParameters": query or {},
        "body":                  json.dumps(body) if body else None,
    }

def print_resp(label, response):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    print(f"  Status : {response['statusCode']}")
    body = json.loads(response["body"])
    print(f"  Body   : {json.dumps(body, indent=4)}")
    return body


# ── Mock S3 client so no real AWS needed ──────────────────────────────────────
mock_s3 = MagicMock()
mock_s3.generate_presigned_url.side_effect = fake_presigned_url
mock_s3.delete_object.return_value = {}

with patch("boto3.client", return_value=mock_s3):
    import importlib
    import prompt_management.lambda_function as lf
    importlib.reload(lf)   # force re-import with mocked boto3

# Point lf.s3 at our mock after reload
lf.s3 = mock_s3

created_id = None

# ── TEST 1: CREATE (no file) ───────────────────────────────────────────────────
event = make_event("POST", "/prompts", body={
    "organization_id":    1,
    "prompt_name":        "System Prompt v1",
    "prompt_description": "Initial system prompt for code review",
})
body = print_resp("POST /prompts (no file)", lf.lambda_handler(event, {}))
if body.get("prompt"):
    created_id = body["prompt"]["id"]
    print(f"  >> Created prompt ID: {created_id}")

# ── TEST 2: CREATE (with file) ────────────────────────────────────────────────
event = make_event("POST", "/prompts", body={
    "organization_id":    1,
    "prompt_name":        "Review Prompt",
    "prompt_description": "Prompt with attached file",
    "file_name":          "review_prompt.txt",
})
body = print_resp("POST /prompts (with file_name → presigned URL)", lf.lambda_handler(event, {}))
if body.get("upload_url"):
    print(f"  >> upload_url: {body['upload_url']}")

# ── TEST 3: LIST ALL ──────────────────────────────────────────────────────────
event = make_event("GET", "/prompts")
print_resp("GET /prompts (list all)", lf.lambda_handler(event, {}))

# ── TEST 4: LIST BY ORG ───────────────────────────────────────────────────────
event = make_event("GET", "/prompts", query={"organization_id": "1"})
print_resp("GET /prompts?organization_id=1", lf.lambda_handler(event, {}))

# ── TEST 5: GET ONE ───────────────────────────────────────────────────────────
if created_id:
    event = make_event("GET", f"/prompts/{created_id}", path_params={"id": str(created_id)})
    print_resp(f"GET /prompts/{created_id}", lf.lambda_handler(event, {}))

# ── TEST 6: GET ONE (not found) ───────────────────────────────────────────────
event = make_event("GET", "/prompts/9999", path_params={"id": "9999"})
print_resp("GET /prompts/9999 (not found)", lf.lambda_handler(event, {}))

# ── TEST 7: UPDATE (metadata only) ────────────────────────────────────────────
if created_id:
    event = make_event("PUT", f"/prompts/{created_id}", path_params={"id": str(created_id)}, body={
        "prompt_description": "Updated description — no file change",
    })
    print_resp(f"PUT /prompts/{created_id} (metadata only)", lf.lambda_handler(event, {}))

# ── TEST 8: UPDATE (with new file) ────────────────────────────────────────────
if created_id:
    event = make_event("PUT", f"/prompts/{created_id}", path_params={"id": str(created_id)}, body={
        "prompt_name": "System Prompt v2",
        "file_name":   "system_prompt_v2.txt",
    })
    body = print_resp(f"PUT /prompts/{created_id} (with new file)", lf.lambda_handler(event, {}))
    if body.get("upload_url"):
        print(f"  >> new upload_url: {body['upload_url']}")

# ── TEST 9: GET UPLOAD URL ────────────────────────────────────────────────────
if created_id:
    event = make_event(
        "GET", f"/prompts/{created_id}/upload-url",
        path_params={"id": str(created_id)},
        query={"file_name": "v3_prompt.txt"},
    )
    body = print_resp(f"GET /prompts/{created_id}/upload-url", lf.lambda_handler(event, {}))

# ── TEST 10: DELETE ───────────────────────────────────────────────────────────
if created_id:
    event = make_event("DELETE", f"/prompts/{created_id}", path_params={"id": str(created_id)})
    print_resp(f"DELETE /prompts/{created_id}", lf.lambda_handler(event, {}))

# ── TEST 11: GET AFTER DELETE ─────────────────────────────────────────────────
if created_id:
    event = make_event("GET", f"/prompts/{created_id}", path_params={"id": str(created_id)})
    print_resp(f"GET /prompts/{created_id} (after delete — should 404)", lf.lambda_handler(event, {}))

print("\n✅  All tests done.\n")
