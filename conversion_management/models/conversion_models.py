from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# 🔹 Common fields (shared)
class BaseConversion(BaseModel):
    id: int
    promptType: str
    date: datetime
    status: str  # 'success' | 'failed'
    s3Input: Optional[str]


# 🔹 Admin schema
class ConversionLog(BaseConversion):
    userId: int
    user: str
    organizationId: int
    organizationName: str
    companyId: int
    companyName: str
    creditUsage: float
    failLog: Optional[str]


# 🔹 User schema
class Conversion(BaseConversion):
    tokenUsage: int
    s3Output: Optional[str]
    processingTime: datetime
