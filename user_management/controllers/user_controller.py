import json
from services.user_service import UserService

class UserController:
    @staticmethod
    def create_user(event):
        try:
            path_params = event.get("pathParameters") or {}
            org_id = path_params.get("orgId")
            company_id = path_params.get("companyId")

            if not org_id or not company_id:
                return UserController._build_response(
                    400, {"error": "Organization ID is required in path."}
                )

            body = json.loads(event.get("body", "{}"))

            # Call Service
            new_user = UserService.create_organization_user(org_id, company_id, body)

            return UserController._build_response(201, {
                "message": "User created successfully",
                "user": new_user
            })

        except ValueError as ve:
            return UserController._build_response(400, {"error": str(ve)})
        except Exception as e:
            return UserController._build_response(500, {"error": str(e)})

    @staticmethod
    def _build_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(body)
        }

    @staticmethod
    def get_users(event):
        try:
            path_params = event.get("pathParameters") or {}
            org_id = path_params.get("orgId")
            company_id = path_params.get("companyId")
            
            #pagination parameters
            query_params = event.get("queryStringParameters") or {}
            page = int(query_params.get("page", 1))
            limit = int(query_params.get("limit", 10))

            if not org_id or not company_id:
                return UserController._build_response(
                    400, {"error": "Organization ID and Company ID are required."}
                )

            result = UserService.get_organization_users(org_id, company_id, page, limit)
            return UserController._build_response(200, result)

        except Exception as e:
            return UserController._build_response(500, {"error": str(e)})

    @staticmethod
    def get_user_by_id(event):
        try:
            path_params = event.get("pathParameters") or {}
            org_id = path_params.get("orgId")
            company_id = path_params.get("companyId")
            user_id = path_params.get("userId")

            if not org_id or not user_id:
                return UserController._build_response(
                    400, {"error": "Organization ID and User ID are required in path."}
                )

            user = UserService.get_user_by_id(org_id, company_id, user_id)

            return UserController._build_response(200, {"user": user})

        except ValueError as ve:
            return UserController._build_response(404, {"error": str(ve)})
        except Exception as e:
            return UserController._build_response(500, {"error": str(e)})
        
    @staticmethod
    def update_user(event):
        try:
            path_params = event.get("pathParameters") or {}
            org_id = path_params.get("orgId")
            company_id = path_params.get("companyId")

            if not org_id:
                return UserController._build_response(
                    400, {"error": "Organization ID is required in path."}
                )

            body = json.loads(event.get("body", "{}"))

            updated_user = UserService.update_user(org_id, company_id, body)

            return UserController._build_response(
                200,
                {
                    "message": "User updated successfully",
                    "user": updated_user
                }
            )

        except ValueError as ve:
            return UserController._build_response(404, {"error": str(ve)})
        except Exception as e:
            return UserController._build_response(500, {"error": str(e)})
        
    @staticmethod
    def delete_user(event):
        try:
            path_params = event.get("pathParameters") or {}
            org_id = path_params.get("orgId")
            company_id = path_params.get("companyId")
            user_id = path_params.get("userId")

            if not org_id or not user_id:
                return UserController._build_response(
                    400, {"error": "Organization ID and User ID are required in path."}
                )
            
            UserService.delete_user(org_id, company_id, user_id)

            return UserController._build_response(
                200,
                {"message": "User deleted successfully"}
            )

        except ValueError as ve:
            return UserController._build_response(404, {"error": str(ve)})
        except Exception as e:
            return UserController._build_response(500, {"error": str(e)})