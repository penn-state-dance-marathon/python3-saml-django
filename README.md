![Build Status](https://github.com/penn-state-dance-marathon/python3-saml-django/workflows/Test%20and%20Build/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/penn-state-dance-marathon/python3-saml-django/branch/master/graph/badge.svg)](https://codecov.io/gh/penn-state-dance-marathon/python3-saml-django)
[![PyPI version](https://badge.fury.io/py/python3-saml-django.svg)](https://badge.fury.io/py/python3-saml-django)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/python3-saml-django)
# Django SAML Toolkit
Quickly and easily add SAML Single Sign-On to your Django projects.
This package is designed to be very simple for initial setup while also being easily customizable to meet all of your needs.

## Installation

### Dependencies (Linux)

The package xmlsec1 is required for this to work.

#### Debian / Ubuntu:

`sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl`

#### Red Hat / CentOs:

`sudo yum install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel`

### Dependencies (Windows)

The python-xmlsec package on Windows is having some issues with hosting, so you can install it manually here:

`pip install
https://github.com/mehcode/python-xmlsec/releases/download/1.3.5/xmlsec-1.3.52.dev0-cp36-cp36m-win_amd64.whl`

For more information [here is the related issue](https://github.com/onelogin/python3-saml/issues/110). 

### Pip

`pip install python3-saml-django`


### Django

Note: Django 1.11 support was dropped in `1.2.0`. If you need Django 1.11 support, please use version `1.1.4`.

**settings.py**

```python
INSTALLED_APPS = [
    ...,
    'django_saml'
]

AUTHENTICATION_BACKENDS = [
    'django_saml.backends.SamlUserBackend',
    ...
]
```

**urls.py**

```python
urlpatterns = [
    path('saml/', include('django_saml.urls')),
    ...
]
```

## Configuration

### Required Settings
**SP Information**

You must provide information about your site to be published as metadata.
```python
SAML_SP = {
    "entityId": "https://<your_site>/saml/metadata/",
    "assertionConsumerService": {
        "url": "https://<your_site>/saml/acs/",
        # DO NOT CHANGE THIS
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "singleLogoutService": {
        "url": "https://<your_site>/saml/sls/",
        # DO NOT CHANGE THIS
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified",
    "x509cert": "<can also be loaded by file, see SAML_BASE_DIRECTORY>",
    "privateKey": "<can also be loaded by file, see SAML_BASE_DIRECTORY>"
}
```

**IdP Information**

You must provide information about the IdP you will be using through one of the following means:
```python
SAML_IDP = {
    "entityId": "https://example.com/saml/metadata/",
    "singleSignOnService": {
        "url": "https://example.com/trust/saml2/http-post/sso/",
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "singleLogoutService": {
        "url": "https://example.com/trust/saml2/http-redirect/slo/",
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "x509cert": "<cert here>"
}
SAML_IDP_FILE = os.path.join(BASE_DIR, 'idp_meta.xml')
SAML_IDP_URL = 'https://example.com/saml/metadata/'
```

### Optional Settings

| Setting | Description | Default | Example |
| ------- | ----------- | ------- | ------- |
| SAML_STRICT | Incorrect SAML responses should be rejected.  **Should be True in production.** | True |  
| SAML_DEBUG | SAML warnings are displayed | False | 
| SAML_CREATE_USER | New users are created on login if they don't exist | True | 
| SAML_UPDATE_USER | Existing users are updated with information from SAML on login | False | 
| SAML_IDP_METADATA_TIMEOUT | If using SAML_IDP_URL, the result will be cached for this many seconds before checking again. | 3600 | 
| SAML_SECURITY | Advanced security settings | See below | See below |
| SAML_CONTACT | Contact information for site maintainers | None | See below |
| SAML_ORGANIZATION | Organization information | None | See below |
| SAML_LOGIN_REDIRECT | Path to redirect users after a successful login | '/' | 
| SAML_LOGOUT_REDIRECT | Path to redirect users after a successful logout | '/logged-out' |
| SAML_NO_USER_REDIRECT | Path to redirect users if SAML_CREATE_USER = False and the user doesn't exist | None (Raises PermissionDenied) | '/permission-error' |
| SAML_USERNAME_ATTR | SAML attribute to use to look up users (name, not friendly name) | 'uid' | 'email' |
| SAML_ATTR_MAP | List of 2-tuples to map SAML attributes to Django user attributes (indexed by name, not friendly name)  | [] | [('givenName', 'first_name')] |
| SAML_ATTR_DEFAULTS | Dictionary of default values to use if an attribute is not present in the SAML response. If no default exists, then a `MissingAttributeException` will be thrown. | {} | {'first_name': ''} |
| SAML_ATTR_UPDATE_IGNORE | List of Django user attributes to only set on first login, and ignore in future logins (only used if SAML_UPDATE_USER is `True`) | [] | [('email', 'first_name')] |
| SAML_BASE_DIRECTORY | File path to load SP certificates.  **Must contain a 'certs' folder with 'sp.key' and 'sp.crt' inside.** | None | `os.path.join(BASE_DIR, 'saml')` |
| SAML_DESTINATION_HOST | Static value to compare with the SAML Destination attribute instead of reading from the request.  Useful for load balancers. | None | 'example.com'
| SAML_DESTINATION_HTTPS | Companion for SAML_DESTINATION_HOST. Set to True if the destination will be over HTTPS but the final request will not be. | None | True
| SAML_DESTINATION_PORT | Companion for SAML_DESTINATION_HOST. Set to a STRING of a number if you use a non-standard port that does not match SAML_DESTINATION_HTTPS. | None | '8080'

**SAML_SECURITY** Default and Example
```python
SAML_SECURITY = {
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
}
```

**SAML_CONTACT** Example
```python
SAML_CONTACT = {
    "technical": {
        "givenName": "Technology Director",
        "emailAddress": "technology@thon.org"
    },
    "support": {
        "givenName": "Lead Systems Admin",
        "emailAddress": "systems@thon.org"
    }
}
```

**SAML_ORGANIZATION** Example
```python
SAML_ORGANIZATION = {
    'en-US': {
        'name': 'thon', 
        'displayname': 'THON', 
        'url': 'thon.org'
    }
}
```

### A Note About Attributes
All SAML attributes must have a name, but sometimes they may have a `FriendlyName`. All of the configuration settings in this library rely on the normal name, not friendly name. Please reference your IdP's attribute settings or analyze a SAML response to see the attributes available.  
Some IdPs use obscure names like `urn:oid:2.5.4.42` while others use `firstName`; just because the docs use a friendly-looking name does not mean it is the `FriendlyName`.

### Advanced Configuration (Custom Backend)
For situations like advanced attribute mapping with groups, transforming SAML attributes, etc, you can create custom backends to use instead of the default.

Example:
```python
from django.contrib.auth.models import Group
from django_saml.backends import SamlUserBackend


class CustomSamlBackend(SamlUserBackend):

    def clean_username(self, username):
        """Return the first part of the email address.
        
        Example: test@example.com -> test.
        """
        return username.split('@')[0]

    def configure_user(self, session_data, user, ignore_fields=None):
        """Custom attribute mapping with groups.
        
        NOTE: ALL SAML attributes in session_data are arrays, even if there is only one element.        
        """
        # Call super() to take care of the simple attribute mapping in SAML_ATTR_MAP
        user = super(CustomSamlBackend, self).configure_user(session_data, user, ignore_fields=ignore_fields)
        for group_name in session_data['psMemberOf']:
            group_name = group_name[5:]
            g = Group.objects.get(name=group_name)
            g.user_set.add(user)
        return user
``` 


## Credit

This project is a wrapper around [OneLogin's python3-saml library](https://github.com/onelogin/python3-saml/).

## Support

If you would like to support the development of this package, please consider [donating to THON](https://donate.thon.org/index.cfm?fuseaction=donorDrive.event&eventID=1868) and supporting our mission.
