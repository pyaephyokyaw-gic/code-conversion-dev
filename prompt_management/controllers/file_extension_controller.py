"""
File Extension Controller
Handles HTTP request/response for file extension operations
"""
from models.response import success, server_error
from services.file_extension_service import (
    get_all_extensions,
    get_input_extensions,
    get_output_extensions
)


def handle_list_all(query_params):
    """GET /prompts/file-extensions - List all file extensions."""
    data, err = get_all_extensions()
    if err:
        return server_error(err)
    return success(data)


def handle_list_input(query_params):
    """GET /prompts/input-extensions - List input file extensions."""
    data, err = get_input_extensions()
    if err:
        return server_error(err)
    return success(data)


def handle_list_output(query_params):
    """GET /prompts/output-extensions - List output file extensions."""
    data, err = get_output_extensions()
    if err:
        return server_error(err)
    return success(data)
