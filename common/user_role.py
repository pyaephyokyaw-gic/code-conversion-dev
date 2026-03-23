from enum import Enum


class UserRole(str, Enum):
    SYSTEM_ADMIN = 'system_admin'
    ORG_ADMIN = 'org_admin'
    MEMBER = 'member'
