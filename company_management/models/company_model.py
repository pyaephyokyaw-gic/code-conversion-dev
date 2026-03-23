class Company:
    def __init__(self, organization_id, name, domain=None, description=None):
        self.organization_id = organization_id
        self.name = name
        self.domain = domain
        self.description = description