from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class SamlUserBackend(ModelBackend):

    def authenticate(self, request, session_data=None, **kwargs):
        if session_data is None:
            return None
        return get_user_model().objects.get(username='dmh6029')
