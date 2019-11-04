from django.apps import AppConfig
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.settings import OneLogin_Saml2_Settings


class DjangoSamlConfig(AppConfig):
    name = 'django_saml'

    def ready(self):
        from . import settings as defaults
        from django.conf import settings
        from django.core.cache import cache
        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
        idp_data = cache.get('SAML_IDP_INFO', None)
        if idp_data is None:
            idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(settings.IDP_METADATA_URL, entity_id='http://192.168.99.100:8080/simplesaml/saml2/idp/metadata.php')
            cache.set('SAML_IDP_INFO', idp_data, settings.IDP_METADATA_TIMEOUT)
        settings.SAML_SETTINGS['idp'] = idp_data['idp']
        settings.ONELOGIN_SAML_SETTINGS = OneLogin_Saml2_Settings(settings.SAML_SETTINGS)
