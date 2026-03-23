from fastapi import HTTPException
from conversion_management.repositories.conversion_repository import ConversionRepository


def get_current_user(event):
    # Placeholder until JWT integration is restored.
    cognito_id = "e7b4eaf8-d091-70ab-374a-bcc90a660643"
    user = ConversionRepository.get_user_by_cognito_id(cognito_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
