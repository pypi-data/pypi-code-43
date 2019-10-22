def link_organizations_to_session(backend, details, response, *args, **kwargs):
    organizations = details["presspass_organizations"]
    session = kwargs["request"].session
    session["presspass_organizations"] = organizations
    session["presspass_authenticated"] = True
    return details
