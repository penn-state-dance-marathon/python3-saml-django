from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class SamlUserBackend(ModelBackend):
    """Backend for logging in users through SAML responses."""

    def authenticate(self, request=None, session_data=None, **kwargs):
        """Handle logging in a user based on SAML data."""
        if session_data is None:
            return None

        username = session_data[settings.SAML_USERNAME_ATTR][0]
        username = self.clean_username(username)

        if settings.SAML_CREATE_USER:
            user, created = UserModel._default_manager.get_or_create(**{
                UserModel.USERNAME_FIELD: username
            })
            if created or settings.SAML_UPDATE_USER:
                args = (session_data, user)
                user = self.configure_user(*args)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
                if settings.SAML_UPDATE_USER:
                    args = (session_data, user)
                    user = self.configure_user(*args)
            except UserModel.DoesNotExist:
                return None
        return user if self.user_can_authenticate(user) else None

    def clean_username(self, username):
        """Perform any cleaning on the "username" prior to using it to get or create the user object.

        By default return unchanged.
        """
        return username

    def configure_user(self, session_data, user):
        """Configure a user after creation and return the updated user.

        By default, apply SAML attribute mapping and set an unusable password for the user.
        """
        for saml_attr, django_attr in settings.SAML_ATTR_MAP:
            setattr(user, django_attr, session_data[saml_attr][0])
        user.set_unusable_password()
        user.save()
        return user
