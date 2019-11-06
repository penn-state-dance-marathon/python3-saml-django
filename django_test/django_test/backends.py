from django_saml.backends import SamlUserBackend


class CustomSamlBackend(SamlUserBackend):
    """Custom SAML backend for handling emails as usernames."""

    def clean_username(self, username):
        """Return the first part of the email address."""
        return username.split('@')[0]
