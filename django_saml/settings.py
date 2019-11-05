from django.contrib.auth import get_user_model

SAML_SETTINGS = {
    "strict": False,
    "debug": True,
    "sp": {
        "entityId": "http://127.0.0.1:8000/saml/metadata/",
        "assertionConsumerService": {
            "url": "http://192.168.99.100:8000/saml/acs/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        "x509cert": "",
        "privateKey": ""
    },
    "security": {
        "nameIdEncrypted": False,
        "authnRequestsSigned": False,
        "logoutRequestSigned": False,
        "logoutResponseSigned": False,
        "signMetadata": False,
        "wantMessagesSigned": False,
        "wantAssertionsSigned": False,
        "wantNameId": True,
        "wantNameIdEncrypted": False,
        "wantAssertionsEncrypted": False,
        "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
        "digestAlgorithm": "http://www.w3.org/2000/09/xmldsig#sha1"
    },
    "contactPerson": {
        "technical": {
            "givenName": "technical_name",
            "emailAddress": "technical@example.com"
        },
        "support": {
            "givenName": "support_name",
            "emailAddress": "support@example.com"
        }
    },
    "organization": {
        "en-US": {
            "name": "thon_test",
            "displayname": "THON Test",
            "url": "https://thon.org"
        }
    }
}

IDP_METADATA_URL = 'http://192.168.99.100:8080/simplesaml/saml2/idp/metadata.php'
IDP_METADATA_TIMEOUT = 3600
SAML_DEFAULT_REDIRECT = '/'
SAML_USERNAME_ATTR = 'uid'
SAML_ATTR_MAP = []