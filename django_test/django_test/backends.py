from django_saml.backends import SamlUserBackend


class CustomSamlBackend(SamlUserBackend):

    def clean_username(self, username):
        return username.split('@')[0]
