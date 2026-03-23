from services import company_service as service
from repositories.company_repository import create_company_table


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
def handle_create(body):
    data, err = service.create_company(body)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# LIST
# ─────────────────────────────────────────────
def handle_list(params):
    data, err = service.list_companies(params)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# GET BY ID
# ─────────────────────────────────────────────
def handle_get(company_id):
    try:
        company_id = int(company_id)
    except:
        return {"error": "Invalid company id"}

    data, err = service.get_company_by_id(company_id)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────
def handle_update(company_id, body):
    try:
        company_id = int(company_id)
    except:
        return {"error": "Invalid company id"}

    data, err = service.update_company(company_id, body)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────
def handle_delete(company_id):
    try:
        company_id = int(company_id)
    except:
        return {"error": "Invalid company id"}

    data, err = service.delete_company(company_id)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
def handle_search(params):
    data, err = service.search_companies(params)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# BY ORGANIZATION
# ─────────────────────────────────────────────
def handle_by_organization(params):
    data, err = service.get_companies_by_organization(params)

    if err:
        return {"error": err}

    return data


# ─────────────────────────────────────────────
# CREATE TABLE
# ─────────────────────────────────────────────
def handle_create_table():
    return create_company_table()