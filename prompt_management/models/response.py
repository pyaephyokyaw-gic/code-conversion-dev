"""
Response Model
Standardized API response helpers
"""
import json


def resp(status, body):
    """Create a standardized API response."""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=str),
    }


def success(data, status=200):
    """Return a success response."""
    return resp(status, data)


def error(message, status=400):
    """Return an error response."""
    return resp(status, {"error": message})


def created(data):
    """Return a 201 Created response."""
    return resp(201, data)


def not_found(message="Resource not found"):
    """Return a 404 Not Found response."""
    return resp(404, {"error": message})


def forbidden(message="Access forbidden"):
    """Return a 403 Forbidden response."""
    return resp(403, {"error": message})


def server_error(message="Internal server error"):
    """Return a 500 Internal Server Error response."""
    return resp(500, {"error": message})
