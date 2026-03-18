"""
File Extension Service
Returns static list of file extensions (no database table)
"""

# Static list of supported file extensions
FILE_EXTENSIONS = [
    {"id": 1, "name": "Python", "extension": ".py"},
    {"id": 2, "name": "COBOL", "extension": ".cbl"},
    {"id": 3, "name": "Java", "extension": ".java"},
    {"id": 4, "name": "JavaScript", "extension": ".js"},
    {"id": 5, "name": "TypeScript", "extension": ".ts"},
    {"id": 6, "name": "C#", "extension": ".cs"},
    {"id": 7, "name": "C++", "extension": ".cpp"},
    {"id": 8, "name": "C", "extension": ".c"},
    {"id": 9, "name": "Go", "extension": ".go"},
    {"id": 10, "name": "Rust", "extension": ".rs"},
    {"id": 11, "name": "Ruby", "extension": ".rb"},
    {"id": 12, "name": "PHP", "extension": ".php"},
    {"id": 13, "name": "SQL", "extension": ".sql"},
    {"id": 14, "name": "Shell", "extension": ".sh"},
    {"id": 15, "name": "PowerShell", "extension": ".ps1"},
]


def get_all_extensions():
    """Get all file extensions."""
    return {"file_extensions": FILE_EXTENSIONS}, None


def get_input_extensions():
    """Get file extensions for input dropdown."""
    return {"input_extensions": FILE_EXTENSIONS}, None


def get_output_extensions():
    """Get file extensions for output dropdown."""
    return {"output_extensions": FILE_EXTENSIONS}, None
