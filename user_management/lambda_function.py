import json
from controllers.user_controller import UserController

def lambda_handler(event, context):
    """
    Main entry point for User Management.
    Routes incoming API Gateway requests to the appropriate Controller method.
    """
    http_method = event.get("httpMethod")
    resource = event.get("resource")

    try:
        # Route: POST /organization/{id}/users
        if http_method == "POST" and resource == "/organization/{orgId}/companies/{companyId}/users":
            return UserController.create_user(event)
            
        # Route: GET /organization/{id}/users
        elif http_method == "GET" and resource == "/organization/{orgId}/companies/{companyId}/users":
            return UserController.get_users(event) 

        # Route: GET /organization/{id}/users/{userId}
        elif http_method == "GET" and resource == "/organization/{orgId}/companies/{companyId}/users/{userId}":
            # return UserController.get_user_by_id(event)
            return UserController.get_user_by_id(event)

        # Route: PUT /organization/{id}/users
        elif http_method == "PUT" and resource == "/organization/{orgId}/companies/{companyId}/users":
            # return UserController.update_user(event)
            return UserController.update_user(event)

        # Route: DELETE /organization/{id}/users
        elif http_method == "DELETE" and resource == "/organization/{orgId}/companies/{companyId}/users/{userId}":
            # return UserController.delete_user(event)
            return UserController.delete_user(event)

        # Fallback for unmatched routes
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": f"Route {http_method} {resource} not found."})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }

def _not_implemented_response(method, resource):
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": f"{method} {resource} is under construction."})
    }
