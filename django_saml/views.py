from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


def prepare_django_request(request):
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return result


def login(request):
    req = prepare_django_request(request)
    auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    if 'next' in request.GET:
        redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + request.GET['next']
        url = auth.login(redirect_to)
    else:
        url = auth.login()
    return HttpResponseRedirect(url)


@csrf_exempt
def saml_acs(request):
    req = prepare_django_request(request)
    saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    request_id = None
    if 'AuthNRequestID' in request.session:
        request_id = request.session['AuthNRequestID']
    saml_auth.process_response(request_id=request_id)

    errors = saml_auth.get_errors()

    if not errors:
        user = auth.authenticate(session_data=saml_auth.get_attributes())
        if user is None:
            raise PermissionDenied()
        auth.login(request, user)
        if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
            return HttpResponseRedirect(saml_auth.redirect_to(req['post_data']['RelayState']))
        else:
            return HttpResponseRedirect(settings.SAML_DEFAULT_REDIRECT)
    return HttpResponseServerError(content=', '.join(errors))


def metadata(request):
    metadata = settings.ONELOGIN_SAML_SETTINGS.get_sp_metadata()
    errors = settings.ONELOGIN_SAML_SETTINGS.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp
