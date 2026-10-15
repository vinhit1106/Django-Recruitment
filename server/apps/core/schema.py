"""Small OpenAPI post-processing rules for public contracts."""


def postprocess_registration_schema(result, generator, request, public):
    """Keep the public registration role enum separate from the User role enum.

    The same ``role`` property name is used by the user model elsewhere. The
    generated component would otherwise reuse the broader User enum and expose
    ``ADMIN`` as a registration option even though the endpoint rejects it.
    """

    schemas = result.get("components", {}).get("schemas", {})
    register = schemas.get("RegisterRequest") or schemas.get("Register")
    if register and register.get("properties", {}).get("role"):
        register["properties"]["role"] = {
            "type": "string",
            "enum": ["CANDIDATE", "EMPLOYER"],
            "default": "CANDIDATE",
            "description": "Public registration role. ADMIN accounts cannot be created through this endpoint.",
        }
    return result
