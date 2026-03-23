from datetime import datetime

class UserModel:
    @staticmethod
    def format_user_data(org_id, company_id, data):
        """Formats and validates raw input into a structured user dictionary."""
        return {
            "organization_id": int(org_id),
            "company_id": int(company_id),
            "name": data.get("name"),
            "email": data.get("email"),
            "role": data.get("role"), 
            "cognito_id": data.get("cognito_id", "dummy-cognito-id-12345"), # Dummy default
            "created_at": datetime.utcnow()
        }