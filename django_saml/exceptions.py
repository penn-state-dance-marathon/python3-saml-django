

class MissingAttributeException(Exception):
    """Thrown when a SAML attribute is expected but missing in the IdP response."""

    pass
