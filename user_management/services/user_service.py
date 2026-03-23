from models.user_model import UserModel
from repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    def create_organization_user(org_id, company_id, payload):
        # 1. Validate mandatory fields (Now including role)
        required_fields = ["name", "email", "role"]
        for field in required_fields:
            if not payload.get(field):
                raise ValueError(f"Missing required field: {field}")

        # 2. Format data via Model (which applies the dummy Cognito ID)
        user_data = UserModel.format_user_data(org_id,company_id, payload)

        # 3. Save via Repository
        return UserRepository.create_user(user_data)

    @staticmethod
    def get_organization_users(org_id, company_id, page=1, limit=10):
        if not org_id or not company_id:
            raise ValueError("Organization ID and Company ID are required.")
        
        page = max(1, int(page))
        limit = max(1, int(limit))
        return UserRepository.get_users_by_organization(org_id, company_id, page, limit)

    @staticmethod
    def get_user_by_id(org_id, company_id, user_id):
        if not org_id or not company_id or not user_id:
            raise ValueError("Organization ID, Company ID, and User ID are required.")

        user = UserRepository.get_user_by_id(org_id, company_id, user_id)

        if not user:
            raise ValueError("User not found.")

        return user
    
    @staticmethod
    def update_user(org_id, company_id, payload):

        required_fields = ["user_id", "name", "email", "role"]

        for field in required_fields:
            if not payload.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        payload["company_id"] = company_id

        updated_user = UserRepository.update_user(org_id, payload)

        if not updated_user:
            raise ValueError("User not found.")

        return updated_user
    
    @staticmethod
    def delete_user(org_id,company_id, user_id):

        if not org_id or not company_id or not user_id:
            raise ValueError("Organization ID, Company ID, and User ID are required.")

        deleted = UserRepository.delete_user(org_id,company_id, user_id)

        if not deleted:
            raise ValueError("User not found.")